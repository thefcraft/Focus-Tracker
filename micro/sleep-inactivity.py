# add last time to the active so we can determine when the laptop is sleeped. and make a new entry in the database


import ctypes
import time
import threading

# Constants
INACTIVITY_LIMIT = 5  # seconds
# use async or something like this or add this in main loop 
def get_idle_duration():
    """Get the idle time in seconds."""
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]

    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    idle_time = (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0 # curr_time - last_input_time
    return idle_time

def monitor_inactivity():
    while True:
        idle_duration = get_idle_duration()
        if idle_duration > INACTIVITY_LIMIT:
            print("User is inactive.")
        time.sleep(1)  # Check every second

if __name__ == "__main__":
    print("Monitoring user inactivity...")
    monitor_inactivity()
    # monitor_thread = threading.Thread(target=monitor_inactivity, daemon=True)
    # monitor_thread.start()

    # # Keep the main program running
    # while True:
    #     time.sleep(1)
