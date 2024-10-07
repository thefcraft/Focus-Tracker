import os
import csv
from dataclasses import dataclass
from typing import List, Dict
from apps import App # apps.py


@dataclass
class Entry:
    nickname: str
    category_name: str 
    distract_category: str # [Distracting, Productive, Other, Ignore App Usage]
    app_limit: bool 
    usage_limit: int # in minutes
    diffculity: str # [Normal, easy]
    streak: int # app limit streak

# TODO: change category of apps/url
# TODO: daily limit of app/url
# TODO: nickname

class AppsInfo:
    def __init__(self):
        # Load the csv
        self.data: Dict[str, Entry] = {
            "Code.exe": Entry(nickname="Visual Studio Code", category_name="coding")
        }
    def category(self, app: App):
        info = self.data.get(app.name, None)
        return info
    # def fn(self, app: App, *args, **kwargs):
    # app which search/modifies for entries ...
    
if __name__ == "__main__":
    app = App.from_active_window()
    appsinfo = AppsInfo()
    
    print(app)
    print(appsinfo.category(app))
    
    