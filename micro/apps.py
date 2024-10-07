import win32gui
import win32api
import win32con
import win32ui
import win32process
from pywinauto import Application
from PIL import Image
import psutil
import os
from typing import Optional, List, Tuple, Dict, Union, TypeVar, Generic, overload, Callable, NewType

U = TypeVar('U')
def debug(fn: Callable[..., U]) ->  Callable[..., U]: # JUST to annotate debug functions
    def wrapper(*args, **kwargs) -> U:
        print(f"Calling function: {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

Url = NewType('Url', str)
    
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


def extract_chromium_url(app: App):
    supported_browsers = ("chrome.exe", "brave.exe") # ERROR: "msedge.exe"
    is_chromium_based_browser: Callable[[App], bool] = lambda app: app.name in supported_browsers
    assert is_chromium_based_browser(app), "The focused window is not a Chromium based browser."
    try:
        # Connect to the focused Chrome window
        window = Application(backend='uia').connect(handle=app.hwnd)
        dlg = window.top_window()
        # Specify the address bar control title
        address_bar = "Address and search bar"
        url = dlg.child_window(title=address_bar, control_type="Edit").get_value()
        return url
    except Exception as e: 
        raise RuntimeError(f"Error retrieving URL: {e}")
        
if __name__ == "__main__":
    import time; time.sleep(1)
    app = App.from_active_window()
    print(app.name)
    print(app.title)
    print(extract_chromium_url(app))
    # if app.name not in icon_map:
    #     icon_map = (*icon_map, app.name)
    #     app.save_icon(directory=os.path.join(directory, "icon"))
       