import os
import sys
import threading
import speech_recognition as sr
import pyttsx3
import pyautogui
import time
import psutil
import platform
from datetime import datetime

from gui import create_gui, restart_with_theme
from secure_vault import verify_password_and_open_vault

# ══════════════════════════════════════════════════════
#  VALTRIX AI — Main Entry Point
# ══════════════════════════════════════════════════════

# Global references
chat_display = None
waveform = None
analytics = None
root = None
active = False

# Shared TTS engine
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 170)


def speak(text):
    try:
        if chat_display:
            chat_display.add_message("valtrix", text)
    except Exception:
        pass
    try:
        if waveform:
            waveform.set_state("speaking")
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass
    finally:
        try:
            if waveform:
                waveform.set_state("idle")
        except Exception:
            pass


# === Voice Recognition ===
class EnhancedVoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 10

    def calibrate(self, source):
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
        except Exception:
            pass

    def listen(self, source):
        try:
            return self.recognizer.listen(source, timeout=6, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            return None
        except Exception:
            return None


recognizer = EnhancedVoiceRecognizer()


def takeCommand():
    r = recognizer.recognizer
    try:
        with sr.Microphone() as source:
            recognizer.calibrate(source)
            try:
                if chat_display:
                    chat_display.add_message("system", "🎤 Listening...")
                if waveform:
                    waveform.set_state("listening")
            except Exception:
                pass
            audio = recognizer.listen(source)
            if audio is None:
                if waveform:
                    waveform.set_state("idle")
                speak("No speech detected.")
                return "none"
    except Exception:
        if waveform:
            waveform.set_state("idle")
        speak("Microphone not available.")
        return "none"

    if waveform:
        waveform.set_state("idle")
    return attempt_recognition(audio)


def attempt_recognition(audio):
    r = recognizer.recognizer
    try:
        query = r.recognize_google(audio, language='en-in').lower().strip()
        if len(query.split()) < 1:
            speak("Please speak clearly.")
            return "none"
        try:
            if chat_display:
                chat_display.add_message("you", query)
        except Exception:
            pass
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't get that. Please try again.")
        return "none"
    except sr.RequestError:
        speak("Speech service unavailable.")
        return "none"


# === System Monitoring ===
def get_system_info():
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime = str(datetime.now() - boot).split('.')[0]
        return {
            "cpu": cpu, "mem_used": round(mem.used / (1024**3), 2),
            "mem_total": round(mem.total / (1024**3), 2), "mem_pct": mem.percent,
            "disk_used": round(disk.used / (1024**3), 2),
            "disk_total": round(disk.total / (1024**3), 2), "disk_pct": disk.percent,
            "uptime": uptime, "os": f"{platform.system()} {platform.release()}",
        }
    except Exception:
        return None


def update_system_info(cpu_lbl, mem_lbl, disk_lbl, up_lbl, os_lbl,
                       cpu_bar, mem_bar, disk_bar):
    try:
        info = get_system_info()
        if info:
            cpu_lbl.configure(text=f"{info['cpu']}%")
            cpu_bar.set(info['cpu'] / 100)
            mem_lbl.configure(text=f"{info['mem_used']}/{info['mem_total']}GB")
            mem_bar.set(info['mem_pct'] / 100)
            disk_lbl.configure(text=f"{info['disk_used']}/{info['disk_total']}GB")
            disk_bar.set(info['disk_pct'] / 100)
            up_lbl.configure(text=f"⏱ {info['uptime']}")
            os_lbl.configure(text=info['os'])
    except Exception:
        pass
    try:
        if root and root.winfo_exists():
            root.after(2000, lambda: update_system_info(
                cpu_lbl, mem_lbl, disk_lbl, up_lbl, os_lbl, cpu_bar, mem_bar, disk_bar))
    except Exception:
        pass


# === Assistant Loop ===
def assistant_loop():
    global active
    active = True
    try:
        from greeting import greetMe
        greetMe(speak)
    except Exception:
        speak("Hello, I am Valtrix AI.")

    while active:
        query = takeCommand()
        if query == "none":
            continue
        time.sleep(0.3)

        if "sleep mode" in query:
            if analytics: analytics.track("sleep_mode")
            speak("Sleep mode activated")
            break
        elif "hello" in query:
            if analytics: analytics.track("greeting")
            speak("Hello, how are you?")
        elif "fine" in query:
            speak("That's great!")
        elif "thank" in query:
            if analytics: analytics.track("greeting")
            speak("It's my pleasure")
        elif "pause" in query:
            if analytics: analytics.track("media_control")
            pyautogui.press("k")
            speak("Video paused")
        elif "play" in query:
            if analytics: analytics.track("media_control")
            pyautogui.press("k")
            speak("Video played")
        elif "mute" in query:
            if analytics: analytics.track("media_control")
            pyautogui.press("m")
            speak("Video muted")
        elif "volume up" in query:
            if analytics: analytics.track("volume")
            try:
                from keyboardfunction import volumeup
                speak("Turning volume up")
                volumeup()
            except Exception:
                speak("Volume up not available.")
        elif "volume down" in query:
            if analytics: analytics.track("volume")
            try:
                from keyboardfunction import volumedown
                speak("Turning volume down")
                volumedown()
            except Exception:
                speak("Volume down not available.")
        elif "open" in query:
            if analytics: analytics.track("open_app")
            try:
                from openapp import openappweb
                openappweb(query, speak)
            except Exception:
                speak("Unable to open app.")
        elif "close" in query:
            if analytics: analytics.track("close_app")
            try:
                from openapp import closeappweb
                closeappweb(query, speak)
            except Exception:
                speak("Unable to close app.")
        elif "google" in query:
            if analytics: analytics.track("google_search")
            try:
                from SearchNow import searchGoogle
                searchGoogle(query, speak)
            except Exception:
                speak("Google search not working.")
        elif "youtube" in query:
            if analytics: analytics.track("youtube_search")
            try:
                from SearchNow import searchYoutube
                searchYoutube(query, speak)
            except Exception:
                speak("YouTube search not working.")
        elif any(w in query for w in ["what", "when", "where", "who", "whom", "whose", "why", "how"]):
            if analytics: analytics.track("wikipedia")
            try:
                from SearchNow import searchWikipedia
                searchWikipedia(query, speak)
            except Exception:
                speak("Wikipedia not working.")
        elif "deactivate" in query:
            if analytics: analytics.track("deactivate")
            speak("Valtrix AI is going offline")
            try:
                if root:
                    root.quit()
            except Exception:
                pass
            break


def start_thread():
    t = threading.Thread(target=assistant_loop)
    t.daemon = True
    t.start()


def main():
    global chat_display, waveform, analytics, root

    while True:
        root, chat_display, waveform, analytics = create_gui(
            start_thread=start_thread,
            open_vault=lambda: verify_password_and_open_vault(speak),
            update_system_info_func=update_system_info,
            get_system_info_func=get_system_info
        )
        root.mainloop()

        # If theme was changed, loop restarts the GUI
        if restart_with_theme[0] is not None:
            restart_with_theme[0] = None
            continue
        break


if __name__ == "__main__":
    main()