import win32gui
import win32process
import psutil
import time
from typing import Optional

def get_active_window_process()->Optional[psutil.Process]:
    """
    Retrieves the `psutil.Process` object associated with the currently active window.

    This function utilizes the `win32gui` and `win32process` libraries to get the handle of the currently active window and then retrieves the process ID associated with that window. It then uses `psutil` to find and return the `psutil.Process` object for the given process ID.

    Returns:
        Optional[psutil.Process]: A `psutil.Process` object for the process associated with the currently active window, or `None` if the process cannot be found or does not exist.

    Raises:
        None

    Example:
    
        >>> process = get_active_window_process()
        >>> if process:
        >>>     print(f"Active window belongs to process: {process.name()}")
        >>> else:
        >>>     print("No process found for the active window.")
    """
    # Get the handle of the active window
    hwnd = win32gui.GetForegroundWindow()
    
    # Get the process ID associated with the window handle
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # Find the process by PID using psutil
    try:
        process = psutil.Process(pid)
        return process
    except psutil.NoSuchProcess:
        return None

for i in range(10):
    active_app = get_active_window_process()
    if active_app:
        print(f"The active app is: {active_app.name()}")
    else:
        print("No active app found.")
    break
    time.sleep(1)
