import os
import pyautogui
import webbrowser
from time import sleep

openapp = {
    # --- System Tools ---
    "command prompt": "cmd",
    "powershell": "powershell",
    "task manager": "taskmgr",
    "control panel": "control",
    "file explorer": "explorer",
    "device manager": "devmgmt.msc",
    "disk management": "diskmgmt.msc",
    "services": "services.msc",
    "registry editor": "regedit",
    "system configuration": "msconfig",
    "event viewer": "eventvwr",
    "group policy": "gpedit.msc",
    "defragment": "dfrgui",
    "performance monitor": "perfmon",
    "system information": "msinfo32",
    "resource monitor": "resmon",
    "directx diagnostic": "dxdiag",
    "snipping tool": "snippingtool",
    "snip & sketch": "ms-screenclip:",
    "calculator": "calc",
    "paint": "mspaint",
    "wordpad": "write",
    "notepad": "notepad",
    "sticky notes": "stikynot",
    "character map": "charmap",
    "remote desktop": "mstsc",
    "windows security": "windowsdefender:",
    "windows update": "ms-settings:windowsupdate",
    "network connections": "ncpa.cpl",
    "bluetooth settings": "ms-settings:bluetooth",
    "display settings": "desk.cpl",
    "sound settings": "mmsys.cpl",
    "keyboard settings": "control keyboard",
    "mouse settings": "control mouse",
    "date and time": "timedate.cpl",
    "region settings": "intl.cpl",
    "language settings": "ms-settings:regionlanguage",
    "power options": "powercfg.cpl",
    "wifi settings": "ms-settings:network-wifi",
    "ethernet settings": "ms-settings:network-ethernet",
    "vpn settings": "ms-settings:network-vpn",
    "storage settings": "ms-settings:storagesense",
    "privacy settings": "ms-settings:privacy",
    "apps and features": "appwiz.cpl",
    "settings": "ms-settings:",
    # --- Microsoft Office ---
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "access": "msaccess",
    "onenote": "onenote",
    "publisher": "mspub",
    "teams": "teams",
    # --- Browsers ---
    "chrome": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "opera": "opera",
    "brave": "brave",
    # --- Code Editors & Dev Tools ---
    "vscode": "code",
    "visual studio": "devenv",
    "pycharm": "pycharm64",
    "intellij": "idea64",
    "android studio": "studio64",
    "eclipse": "eclipse",
    "netbeans": "netbeans64",
    "jupyter notebook": "jupyter-notebook",
    "git bash": "git-bash",
    "xamp": "xampp-control",
    "docker": "docker",
    "postman": "postman",
    # --- Media Players ---
    "vlc": "vlc",
    "windows media player": "wmplayer",
    "groove music": "mswindowsmusic:",
    "movies and tv": "mswindowsvideo:",
    "spotify": "spotify",
    "itunes": "itunes",
    "audacity": "audacity",
    # --- Communication ---
    "skype": "skype",
    "zoom": "zoom",
    "slack": "slack",
    "discord": "discord",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
    "signal": "signal",
    "google meet": "chrome --app=https://meet.google.com",
    "outlook mail": "outlookmail:",
    # --- Cloud & Storage ---
    "onedrive": "onedrive",
    "google drive": "googledrive",
    "dropbox": "dropbox",
    "mega": "mega",
    "icloud": "icloud",
    # --- Design & Creative ---
    "photoshop": "photoshop",
    "illustrator": "illustrator",
    "after effects": "afterfx",
    "premiere pro": "premiere",
    "lightroom": "lightroom",
    "coreldraw": "coreldraw",
    "canva": "canva",
    "paint 3d": "ms-paint:",
    # --- Utilities ---
    "7zip": "7zfm",
    "winrar": "winrar",
    "virtualbox": "virtualbox",
    "vmware": "vmware",
    "teamviewer": "teamviewer",
    "anydesk": "anydesk",
    "obs studio": "obs64",
    "screen recorder": "ms-screenclip:",
    # --- Gaming & Stores ---
    "steam": "steam",
    "epic games": "epicgameslauncher",
    "xbox": "xbox",
    "rockstar launcher": "launcher",
    "riot client": "riotclientservices",
    "minecraft": "minecraft",
    "valorant": "valorant",
    "fortnite": "fortnite",
    "pubg": "pubg",
    "gta": "gta5"
}


def openappweb(query, speak=None):
    if speak is None:
        speak = print
    speak("Launching...")
    if ".com" in query or ".co.in" in query or ".org" in query:
        query = query.replace("open", "").replace("launch", "").replace(" ", "")
        webbrowser.open(f"https://www.{query}")
    else:
        for app in openapp:
            if app in query:
                os.system(f"start {openapp[app]}")
                return
        speak("Application not found.")


def closeappweb(query, speak=None):
    if speak is None:
        speak = print
    speak("Closing...")
    tab_count = 0

    if "1 tab" in query or "one tab" in query:
        tab_count = 1
    elif "to tab" in query:
        tab_count = 2
    elif "3 tab" in query:
        tab_count = 3
    elif "4 tab" in query:
        tab_count = 4
    elif "5 tab" in query:
        tab_count = 5

    if tab_count > 0:
        for _ in range(tab_count):
            pyautogui.hotkey("ctrl", "w")
            sleep(0.5)
        speak(f"{tab_count} tab(s) closed.")
        return

    for app in openapp:
        if app in query:
            os.system(f"taskkill /f /im {openapp[app]}.exe")
            speak(f"{app} closed.")
            return

    speak("Application not found to close.")
