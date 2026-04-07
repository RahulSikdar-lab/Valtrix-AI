import datetime


def greetMe(speak):
    """Time-based greeting using the shared speak function"""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour <= 12:
        speak("Good Morning")
    elif 12 < hour <= 18:
        speak("Good Afternoon")
    else:
        speak("Good Evening")

    speak("Valtrix AI is now online")