# block the website using dns lookup or from windows dns file i.e., 
# or use some extension
# or use url.py instead and block the connection 

import os, sys
import ctypes

class HostsFileManager:
    def __init__(self, hosts_path=r"C:\Windows\System32\drivers\etc\hosts"):
        self.hosts_path = hosts_path
        
    def is_admin(self):
        """Check if the script is running with administrator privileges."""
        return ctypes.windll.shell32.IsUserAnAdmin()

    def request_admin(self):
        """Re-run the script with administrator privileges."""
        if not self.is_admin():
            print("This script requires administrator privileges.")
            if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1) == 0:
                print("Failed to get administrator privileges.")
                exit(1)
            else:
                exit(0)

    def block_website(self, website):
        """Block a website by adding it to the hosts file."""
        redirection = "127.0.0.1"
        
        try:
            with open(self.hosts_path, 'a') as hosts_file:
                hosts_file.write(f"{redirection} {website}\n")
            print(f"Successfully blocked {website}.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def remove_blocked_website(self, website):
        """Remove a blocked website from the hosts file."""
        try:
            with open(self.hosts_path, 'r') as hosts_file:
                lines = hosts_file.readlines()

            updated_lines = []
            website_found = False
            
            for line in lines:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    parts = stripped_line.split()
                    if (parts[0] == '127.0.0.1' and website in parts[1:]):
                        website_found = True
                        continue
                updated_lines.append(line)

            with open(self.hosts_path, 'w') as hosts_file:
                hosts_file.writelines(updated_lines)

            if website_found:
                print(f"Successfully removed {website} from the blocked websites.")
            else:
                print(f"{website} was not found in the blocked websites.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def list_blocked_websites(self):
        """List all blocked websites from the hosts file."""
        blocked_websites = []

        try:
            with open(self.hosts_path, 'r') as hosts_file:
                for line in hosts_file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if parts[0] == '127.0.0.1' and len(parts) > 1:
                            blocked_websites.extend(parts[1:])

            if blocked_websites:
                print("Blocked websites:")
                for website in blocked_websites:
                    print(website)
            else:
                print("No blocked websites found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # TODO: use args instead and call this script with some arguments or make separate files so when user clicks on admin prevelages then run and close.
    manager = HostsFileManager()
    manager.request_admin()  # Request admin privileges at the start
    
    while True:
        action = input("Choose an action: [block, remove, list, exit]: ").strip().lower()
        
        if action == 'block':
            website = input("Enter the website to block (e.g., example.com): ")
            manager.block_website(website)
        elif action == 'remove':
            website = input("Enter the website to unblock (e.g., example.com): ")
            manager.remove_blocked_website(website)
        elif action == 'list':
            manager.list_blocked_websites()
        elif action == 'exit':
            break
        else:
            print("Invalid action. Please choose 'block', 'remove', 'list', or 'exit'.")