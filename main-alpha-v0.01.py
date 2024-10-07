import win32gui
import win32api
import win32con
import win32ui
import win32process
from PIL import Image
import psutil
import time
import csv
import os
import io, base64
from datetime import datetime
# from collections import namedtuple
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Union, TypeVar, Generic, overload

os.chdir(os.path.dirname(__file__))

# TODO: use sqlite for database ...
# TODO: db.update() or something to save state at runtime or in 10 minutes etc.
# TODO: update if title is changed
# TODO: track inactivity or sleep using end_time... use duration 0(<1) default and save it on database when inactivity or sleep [ handle error when db.update() ]

def get_current_date()->str:
    return datetime.now().strftime('%Y-%m-%d')

def get_current_timestamp()->str:
    return datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

class App:
    def __init__(self, hwnd:int, pid:int):
        self.hwnd:int = hwnd
        self.pid:int = pid
        try: process = psutil.Process(pid)
        except psutil.NoSuchProcess: process = None
        self.process: Optional[psutil.Process] = process
    @classmethod
    def from_active_window(cls)->"App":
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return cls(hwnd, pid)
    @property
    def name(self):
        return self.process.name()
    @property
    def title(self):
        return win32gui.GetWindowText(self.hwnd)
    
    def save_icon(self, directory: str)->bool:
        if not os.path.exists(directory): os.makedirs(directory)
        # Open the process
        hprocess:int = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, self.pid)
        # Get the exe path
        exe_path = win32process.GetModuleFileNameEx(hprocess, 0)
        
        # Extract the icon
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        
        if len(large) == 0 or len(small) == 0: return False
        
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
        return not self.process is None
    
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
                self.title == value.title)
# Entry = namedtuple('Entry', ['program_name', 'window_title', 'timestamp', 'duration'])
@dataclass
class Entry:
    program_name: str
    window_title: str
    timestamp: str
    duration: int
    
    
class Database(List["Entry"]):
    def __init__(self, directory="data"):
        super().__init__()
        self.directory = directory
    def save(self):
        if not os.path.exists(os.path.join(self.directory, "local")): os.makedirs(os.path.join(self.directory, "local"))
        
        data: List[Dict[str, Union[str, int]]] = [
            {"program_name": entry.program_name, 'window_title': entry.window_title, "timestamp": entry.timestamp, "duration": entry.duration}
            for entry in self
        ]
        file_path = os.path.join(self.directory, "local", f"{get_current_date()}.csv")
        
        if os.path.exists(file_path):
            if not os.path.isfile(file_path): raise Exception("File path is directory")
            with open(file_path, mode='r', newline='', encoding='utf') as csvfile:
                reader = list(csv.DictReader(csvfile))
                data = reader + data
        
        with open(file_path, 'w', newline='', encoding='utf') as csvfile:
            fieldnames = ['program_name', 'window_title', 'timestamp', 'duration']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

directory: str = "data"
db:Database = Database(directory=directory)
icon_map:Tuple[str] = ()
 
interval:int = 2
last_app: Optional["App"] = None
while True:
    try: 
        app = App.from_active_window()
        if app:
            if app == last_app: db[-1].duration += interval
            else: 
                db.append(Entry(app.name, app.title, get_current_timestamp(), interval))
                if app.name not in icon_map:
                    icon_map = (*icon_map, app.name)
                    app.save_icon(directory=os.path.join(directory, "icon"))
                    print(icon_map)
                print(db)
                last_app = app
        time.sleep(interval)
    except KeyboardInterrupt: break
    except Exception as e:
        print("Exception during runtime: ", e)
        break
db.save()