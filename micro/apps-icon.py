import win32gui
import win32process
import win32api
import win32con
import win32ui
import os
from PIL import Image

def get_exe_icon(hwnd):
    # Get the process ID
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # Open the process
    process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
    
    # Get the exe path
    exe_path = win32process.GetModuleFileNameEx(process, 0)
    
    # Extract the icon
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
    
    large, small = win32gui.ExtractIconEx(exe_path, 0)
    win32gui.DestroyIcon(small[0])
    
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    hdc = hdc.CreateCompatibleDC()
    
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), large[0])
    
    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGBA',
        (ico_x, ico_y),
        bmpstr, 'raw', 'BGRA', 0, 1
    )
    
    win32gui.DestroyIcon(large[0])
    
    return img

# Get the foreground window
hwnd = win32gui.GetForegroundWindow()

# Get the icon
icon = get_exe_icon(hwnd)

# Save the icon as a PNG file
icon.show()
print("Icon saved as foreground_window_icon.png")