import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import speech_recognition as sr
import pyttsx3
import pyautogui
import time
import psutil
import platform
from datetime import datetime

# Import the separated modules
from gui import create_gui
from secure_vault import SecureVaultStorage, verify_password_and_open_vault

# Global variables for GUI elements
text_display = None
active = False

# === Enhanced Text-to-Speech Setup ===
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 170)

def speak(text):
    try:
        if text_display:
            text_display.insert(tk.END, f"\nAssistant: {text}")
            text_display.yview(tk.END)
    except Exception:
        pass
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

# === Enhanced Voice Recognition with Noise Reduction ===
class EnhancedVoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.setup_recognizer()
        
    def setup_recognizer(self):
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 10
        
    def calibrate_microphone(self, source):
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
            return True
        except Exception as e:
            print(f"Calibration warning: {e}")
            return False
    
    def enhanced_listen(self, source):
        try:
            audio = self.recognizer.listen(
                source, 
                timeout=6, 
                phrase_time_limit=7
            )
            return audio
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"Listening error: {e}")
            return None

enhanced_recognizer = EnhancedVoiceRecognizer()

def takeCommand():
    r = enhanced_recognizer.recognizer
    try:
        with sr.Microphone() as source:
            enhanced_recognizer.calibrate_microphone(source)
            try:
                if text_display:
                    text_display.insert(tk.END, "\n🎤 Listening...")
                    text_display.yview(tk.END)
            except Exception:
                pass
            audio = enhanced_recognizer.enhanced_listen(source)
            if audio is None:
                speak("No speech detected.")
                return "none"
    except Exception as e:
        speak("Microphone not available.")
        return "none"

    query = attempt_recognition(audio)
    return query

def attempt_recognition(audio):
    recognizer = enhanced_recognizer.recognizer
    try:
        query = recognizer.recognize_google(audio, language='en-in')
        query = query.lower().strip()
        if len(query.split()) < 1:
            speak("Please speak clearly.")
            return "none"
        try:
            if text_display:
                text_display.insert(tk.END, f"\nYou: {query}")
                text_display.yview(tk.END)
        except Exception:
            pass
        return query
    except sr.UnknownValueError:
        try:
            query = recognizer.recognize_google(
                audio, 
                language='en-in',
                show_all=False
            )
            if query:
                query = query.lower().strip()
                try:
                    if text_display:
                        text_display.insert(tk.END, f"\nYou: {query}")
                        text_display.yview(tk.END)
                except Exception:
                    pass
                return query
        except:
            pass
        speak("Sorry, I didn't get that clearly. Please try again.")
        return "none"
    except sr.RequestError as e:
        speak("Speech service is currently unavailable.")
        return "none"

# === System Monitoring Functions ===
def get_system_info():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_total = round(memory.total / (1024**3), 2)
        memory_used = round(memory.used / (1024**3), 2)
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024**3), 2)
        disk_used = round(disk.used / (1024**3), 2)
        disk_percent = disk.percent
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = str(uptime).split('.')[0]
        
        system_info = {
            "cpu_usage": cpu_percent,
            "memory_used": memory_used,
            "memory_total": memory_total,
            "memory_percent": memory_percent,
            "disk_used": disk_used,
            "disk_total": disk_total,
            "disk_percent": disk_percent,
            "uptime": uptime_str,
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "os": f"{platform.system()} {platform.release()}",
            "processor": platform.processor()
        }
        
        return system_info
    except Exception as e:
        print(f"Error getting system info: {e}")
        return None

# === Enhanced Core Assistant Loop ===
def assistant_loop():
    global active
    active = True
    try:
        from greeting import greetMe
        greetMe(speak)
    except Exception:
        speak("Hello, I am your Desktop Assistant.")

    while active:
        query = takeCommand()
        if query == "none":
            continue

        time.sleep(0.3)

        if "sleep mode" in query:
            speak("Sleep mode activated")
            break

        elif "hello" in query:
            speak("Hello, how are you?")
        elif "fine" in query:
            speak("That's great!")
        elif "thank" in query:
            speak("It's my pleasure")

        elif "pause" in query:
            pyautogui.press("k")
            speak("Video paused")
        elif "play" in query:
            pyautogui.press("k")
            speak("Video played")
        elif "mute" in query:
            pyautogui.press("m")
            speak("Video muted")
        elif "volume up" in query:
            try:
                from keyboardfunction import volumeup
                speak("Turning volume up")
                volumeup()
            except Exception:
                speak("Volume up function not available.")
        elif "volume down" in query:
            try:
                from keyboardfunction import volumedown
                speak("Turning volume down")
                volumedown()
            except Exception:
                speak("Volume down function not available.")
        elif "open" in query:
            try:
                from openapp import openappweb
                openappweb(query)
            except Exception:
                speak("Unable to open app.")
        elif "close" in query:
            try:
                from openapp import closeappweb
                closeappweb(query)
            except Exception:
                speak("Unable to close app.")
        elif "google" in query:
            try:
                from SearchNow import searchGoogle
                searchGoogle(query)
            except Exception:
                speak("Google search not working.")
        elif "youtube" in query:
            try:
                from SearchNow import searchYoutube
                searchYoutube(query)
            except Exception:
                speak("YouTube search not working.")
        elif any(word in query for word in ["what", "when", "where", "who", "whom", "whose", "why", "how"]):
            try:
                from SearchNow import searchWikipedia
                searchWikipedia(query)
            except Exception:
                speak("Wikipedia not working.")

        elif "deactivate" in query:
            speak("Desktop Assistant is going offline")
            os._exit(0)

def start_thread():
    thread = threading.Thread(target=assistant_loop)
    thread.daemon = True
    thread.start()

def main():
    global text_display
    root, text_display = create_gui(
        start_thread=start_thread,
        open_vault=verify_password_and_open_vault,
        update_system_info_func=update_system_info,
        get_system_info_func=get_system_info
    )
    root.mainloop()

def update_system_info(cpu_label, memory_label, disk_label, uptime_label, os_label, cpu_bar, memory_bar, disk_bar):
    """Update system information display with safe element access"""
    try:
        info = get_system_info()
        if not info:
            return
            
        if cpu_label and cpu_bar:
            cpu_label.config(text=f"CPU: {info['cpu_usage']}%")
            cpu_bar['value'] = info['cpu_usage']
        
        if memory_label and memory_bar:
            memory_label.config(text=f"RAM: {info['memory_used']}/{info['memory_total']}GB ({info['memory_percent']}%)")
            memory_bar['value'] = info['memory_percent']
        
        if disk_label and disk_bar:
            disk_label.config(text=f"Disk: {info['disk_used']}/{info['disk_total']}GB ({info['disk_percent']}%)")
            disk_bar['value'] = info['disk_percent']
        
        if uptime_label:
            uptime_label.config(text=f"Uptime: {info['uptime']}")
        
        if os_label:
            os_label.config(text=f"OS: {info['os']}")
        
    except Exception as e:
        if "uptime_label" in str(e) or "cpu_label" in str(e):
            pass
        else:
            print(f"Error updating system info: {e}")
    
    try:
        if root and root.winfo_exists():
            root.after(2000, lambda: update_system_info(cpu_label, memory_label, disk_label, uptime_label, os_label, cpu_bar, memory_bar, disk_bar))
    except:
        pass

if __name__ == "__main__":
    main()