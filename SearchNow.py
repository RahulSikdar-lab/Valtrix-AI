import pywhatkit
import wikipedia
import webbrowser


def searchGoogle(query, speak=None):
    if speak is None:
        speak = print
    if "google" in query:
        query = query.replace("google search", "")
        query = query.replace("google", "").strip()
        speak("This is what I found on Google")
        try:
            pywhatkit.search(query)
            result = wikipedia.summary(query, 1)
            speak(result)
        except Exception:
            speak("No speakable output available")


def searchYoutube(query, speak=None):
    if speak is None:
        speak = print
    if "youtube" in query:
        speak("This is what I found for your search!")
        query = query.replace("youtube search", "")
        query = query.replace("youtube", "").strip()
        web = "https://www.youtube.com/results?search_query=" + query
        webbrowser.open(web)
        try:
            pywhatkit.playonyt(query)
        except Exception:
            pass
        speak("Done")


def searchWikipedia(query, speak=None):
    if speak is None:
        speak = print
    if any(word in query for word in ["what", "when", "where", "who", "whom", "whose", "why", "how"]):
        speak("Searching from Wikipedia...")
        query = query.replace("search wikipedia", "")
        query = query.replace("wikipedia", "").strip()
        try:
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia...")
            speak(results)
        except Exception:
            speak("Sorry, I couldn't find that on Wikipedia")
