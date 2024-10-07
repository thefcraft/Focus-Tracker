import win32gui
import win32api
import win32con
import win32ui
import win32process
from pywinauto import Application, WindowSpecification
from PIL import Image
import psutil
import time
import csv
import os
import ctypes
import io, base64
from datetime import datetime
# from collections import namedtuple
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Union, TypeVar, Generic, overload, Callable, NewType, Any

# TODO: add total data uses and app wise data uses [if it is without the administration permission]

# TODO: use sqlite for database ...
# TODO: track inactivity or sleep using end_time... use duration 0(<1) default and save it on database when inactivity or sleep [ handle error when db.update() ]

os.chdir(os.path.dirname(__file__))


U = TypeVar('U')
def debug(fn: Callable[..., U]) ->  Callable[..., U]: # JUST to annotate debug functions
    def wrapper(*args, **kwargs) -> U:
        print(f"Calling function: {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

Seconds = NewType('Seconds', int)
Url = NewType('Url', str)

# Constants
INACTIVITY_LIMIT:Seconds = 60*5 # if no input given in last 5 minutes then user is inactive...
INTERVAL:Seconds = 2
SAVE_EVERY:Seconds = 60*10 # save every 10 minutes
assert SAVE_EVERY%INTERVAL == 0, "SAVE_EVERY should be divisible by INTERVAL"

def get_current_date()->str:
    return datetime.now().strftime('%Y-%m-%d')

def get_current_timestamp()->str:
    return datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

# Entry = namedtuple('Entry', ['program_name', 'window_title', 'timestamp', 'duration'])
@dataclass
class Entry:
    program_name: str
    window_title: str
    timestamp: str
    duration: int
    is_inactive: bool # TODO: use this instead so we can track which app leads to inactivity...
    url: Optional[str]
    # no need as i force split db when it sleep or something else i.e., we can do this by sleep monitoring thing or time now and time later difference which must be between inveral or so
    # timestamp_end: Optional[datetime] # datetime no need to save this into database as this is just for internal use 
    
class App:
    def __init__(self, hwnd:int, pid:int):
        assert pid >= 0, "pid must be positive integer"
        
        self.hwnd:int = hwnd
        self.pid:int = pid
        try: 
            process = psutil.Process(pid)
            name = process.name()
        except psutil.NoSuchProcess: 
            # process = None
            name = None
            print("Could not find process somthing went wrong...")
            # Raise error
        # self.process: Optional[psutil.Process] = process # no need to make the process as class attr ...
        self.name: Optional[str] = name
        self.title: str = win32gui.GetWindowText(self.hwnd)
        self._url = None # for self.url property...
        
    def copy(self)->"App":
        instance = App.__new__(App)
        instance.hwnd = self.hwnd
        instance.pid = self.pid
        # instance.process = None
        instance.name = self.name
        instance.title = self.title
        instance._url = self._url
        return instance
        
    @classmethod
    def from_active_window(cls)->"App":
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return cls(hwnd, pid)
    
    def save_icon(self, directory: str)->bool:
        if not os.path.exists(directory): os.makedirs(directory)
        
        # Extract the icon
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        
        large, small = win32gui.ExtractIconEx(self.executable_path, 0)
        
        if len(large) == 0 or len(small) == 0: 
            print("unable to save the icon...")
            return False
        
        win32gui.DestroyIcon(small[0])
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large[0])

        bmpstr = hbmp.GetBitmapBits(True)
        icon = Image.frombuffer( 
            'RGBA',
            (ico_x, ico_y),
            bmpstr, 'raw', 'BGRA', 0, 1
        ) # large icon from exe
        win32gui.DestroyIcon(large[0])
        
        icon.save(os.path.join(directory, f"{self.name}.png"), format="PNG")
        icon.close()
        return True
    
    def __repr__(self) -> str:
        return f"<{self.name}: {self.title}>"

    def __bool__(self):
        return not self.name is None

    @overload
    def __eq__(self, value: "App") -> bool: ...
    @overload
    def __eq__(self, value: Optional[object]) -> bool: ...
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, App):
            if value is None: return not self
            return False
        if not value: return not self
        return (self.hwnd == value.hwnd and 
                self.pid == value.pid and 
                self.name == value.name and 
                self.title == value.title and 
                self.url == value.url)
        
    @property
    def executable_path(self)->str:
        # Open the process
        hprocess:int = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, self.pid)
        # Get the exe path
        return win32process.GetModuleFileNameEx(hprocess, 0)
    
    @property
    def is_chromium_based_browser(self)->bool:
        if not self: return False
        supported_browsers = ("chrome.exe", "brave.exe", "msedge.exe") # ERROR: 
        # is_chromium_based_browser: Callable[[App], bool] = lambda app: app.name in supported_browsers
        return self.name in supported_browsers
    
    @property
    def url(self)->Optional[Url]:
        if self._url is not None: return self._url
        if not self.is_chromium_based_browser: return None
        try:
            # Connect to the focused Chrome window
            window = Application(backend='uia').connect(handle=self.hwnd)
            dlg = window.top_window()
            # Specify the address bar control title
            address_bar = "Address and search bar"
            
            if self.name == "msedge.exe":
                # Search all descendants for microsoft edge
                descendants = dlg.descendants()
                for d in descendants:
                    if d.element_info.control_type == "Edit" and d.element_info.name == address_bar:
                        self._url = d.get_value()
                        return self._url
                    
            d = dlg.child_window(title=address_bar, control_type="Edit")
            self._url = d.get_value()
            return self._url 
        
        except Exception as e: 
            raise RuntimeError(f"Error retrieving URL: {e}")
    
    @debug
    def get_window_gui_debug_info(self) -> dict:
        """Helper method to get UI automation debug info for the window"""
        try:
            window = Application(backend='uia').connect(handle=self.hwnd)
            dlg = window.top_window()
            
            debug_info = {
                "window_title": dlg.window_text(),
                "child_elements": []
            }
            for child in dlg.children():
                child_info = {
                    "control_type": child.element_info.control_type,
                    "name": child.element_info.name,
                    "auto_id": child.element_info.automation_id,
                    "class_name": child.element_info.class_name
                }
                debug_info["child_elements"].append(child_info)
            
            return debug_info
        except Exception as e:
            return {"error": str(e)}
    

def extract_executable_description(app: App):
    file_path = app.executable_path
    dirname = os.path.dirname(file_path)
    name = os.path.basename(dirname) # in general it should be the name
    return name


class Database(List["Entry"]):
    def __init__(self, directory="data", interval:Seconds=1):
        super().__init__()
        self.directory = directory
        self.icons = self.load_icons()
        self.last_app: Optional["App"] = None
        self.last_is_inactive: bool = False
        self.interval = interval
        # self.last_updated: datetime = datetime.now() # to monitor sleeping and so...
        
        self.len_before_commit: Optional[int] = None
    def commit(self):
        if self.len_before_commit is None:
            if not os.path.exists(os.path.join(self.directory, "local")): os.makedirs(os.path.join(self.directory, "local"))
            file_path = os.path.join(self.directory, "local", f"{get_current_date()}.csv")
            if os.path.exists(file_path):
                with open(file_path, mode='r', newline='', encoding='utf') as csvfile:
                    reader = list(csv.DictReader(csvfile))
                    self.len_before_commit = len(reader)
            else:
                self.len_before_commit = 0
                with open(file_path, 'w', newline='', encoding='utf') as csvfile:
                    fieldnames = ['program_name', 'window_title', 'timestamp', 'duration', 'is_inactive', 'url']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
        self.save()
        
    def save(self):
        if not os.path.exists(os.path.join(self.directory, "local")): os.makedirs(os.path.join(self.directory, "local"))
        
        data: List[Dict[str, Union[str, Optional[str], int]]] = [
            {"program_name": entry.program_name, 'window_title': entry.window_title, "timestamp": entry.timestamp, "duration": entry.duration, "is_inactive":entry.is_inactive, "url": entry.url}
            for entry in self
        ]
        file_path = os.path.join(self.directory, "local", f"{get_current_date()}.csv")
        
        if os.path.exists(file_path):
            if not os.path.isfile(file_path): raise Exception("File path is directory")
            with open(file_path, mode='r', newline='', encoding='utf') as csvfile:
                reader = list(csv.DictReader(csvfile))
                data = reader[:0 if self.len_before_commit is None else self.len_before_commit] + data
        
        with open(file_path, 'w', newline='', encoding='utf') as csvfile:
            fieldnames = ['program_name', 'window_title', 'timestamp', 'duration', 'is_inactive', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def load_icons(self)->List[str]:
        if not os.path.exists(os.path.join(self.directory, "icon")): os.makedirs(os.path.join(self.directory, "icon"))
        return os.listdir(os.path.join(self.directory, "icon"))
    
    def safe_add(self, app: App, interval:Seconds, is_inactive: bool=False):
        if (not is_inactive or self.last_is_inactive) and app == self.last_app:     
            self[-1].duration += interval
            return 
        
        if app.name not in self.icons:
            self.icons.append(app.name)
            app.save_icon(directory=os.path.join(self.directory, "icon"))
            
        self.append(Entry(app.name, app.title, get_current_timestamp(), 0, is_inactive=is_inactive, url=app.url)) # duration 0 i.e., <interval (less than interval seconds)
        
        self.last_app = app.copy()
        self.last_is_inactive = is_inactive
    
    def update(self, app: App, is_inactive: bool=False):
        self.safe_add(app, self.interval, is_inactive)
        # self.last_updated = datetime.now()
        time.sleep(self.interval)
        # loop_time = (datetime.now() - self.last_updated).seconds
        # print(loop_time)
        
        
def get_idle_duration()->Seconds:
    """Get the idle time in seconds."""
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]

    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    idle_time = (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0 # curr_time - last_input_time
    return idle_time

def main():
    db:Database = Database(directory="data", interval=INTERVAL)
    idx = 1
    while True:
        idle_duration = get_idle_duration()
        is_inactive:bool = idle_duration > INACTIVITY_LIMIT
        if is_inactive: print("User is inactive.")
        try:
            app = App.from_active_window()
            db.update(app, is_inactive=is_inactive)
            idx+=1
            idx%=(SAVE_EVERY//INTERVAL)
            if idx==0: db.commit() 
        except KeyboardInterrupt: break
        except Exception as e:
            print("Exception during runtime: ", e)
            continue
    db.save()
    
if __name__ == "__main__":
    main()