import win32gui
import time

def get_active_window_title():
    # Get the handle of the active window
    hwnd = win32gui.GetForegroundWindow()
    # Get the title of the active window
    window_title = win32gui.GetWindowText(hwnd)
    
    return window_title
# time.sleep(1)
# Retrieve the title of the currently active window
active_window_title = get_active_window_title()

print(f"Active window title: {active_window_title}")

# If it's Chrome, it will include the active tab's title
if "Google Chrome" in active_window_title:
    print(f"Current Chrome tab: {active_window_title}")
