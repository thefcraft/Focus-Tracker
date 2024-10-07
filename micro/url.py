import win32gui
from pywinauto import Application

def get_active_browser_url():
    # Get the handle of the active window
    hwnd = win32gui.GetForegroundWindow()
    window_text = win32gui.GetWindowText(hwnd)
    print(window_text)
    # Check if the focused window is a Chrome window
    supported_browsers = ("Google Chrome", "Brave", "Microsoft​ Edge")
    if any([w in window_text for w in supported_browsers]): # we can remove this and use add this assertion in the app.exe or something
        try:
            # Connect to the focused Chrome window
            app = Application(backend='uia').connect(handle=hwnd)
            print(app)
            dlg = app.top_window()
            
            # Print all child controls
            for control in dlg.children():
                title = control.window_text()
                control_type = None #control.control_type()
                automation_id = control.automation_id()
                print(f"Title: {title}, Control Type: {control_type}, Automation ID: {automation_id}")
    

            # Specify the address bar control title
            address_bar = "Address and search bar"
            url = dlg.child_window(title=address_bar, control_type="Edit").get_value()
            print(f"Current URL: {url}")
        except Exception as e:
            print(f"Error retrieving URL: {e}")
    else:
        print("The focused window is not a Chromium based browser.")
        
import time; time.sleep(2)
get_active_browser_url()