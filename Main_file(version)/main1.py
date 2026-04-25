import speech_recognition as sr
import os
import pyautogui
import webbrowser
import subprocess
import time
import webview
import threading
import pyttsx3
import queue
import asyncio
from skills.whats_app import vasu_intent_engine, send_whatsapp_action
from brain import get_llm_response


USER_HOME = os.path.expanduser("~")

ACTIVE_SESSION = False
# SESSION_TIMOUT = False
# last_command_time = 0

# List of folders your assistant should search
SEARCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Videos"),
]

# ---------------- NEW SPEAK FUNCTION (pyttsx3) ----------------

class VasuVoice:
    def __init__(self):
        self.word_queue = queue.Queue()
        # Voice Settings
        self.rate = 180
        self.volume = 1.0
        
        # Start the persistent background thread
        threading.Thread(target=self._speak_handler, daemon=True).start()

    def _speak_handler(self):
        """यह लूप कभी क्रैश नहीं होगा और हर सेंटेंस को फ्रेश तरीके से हैंडल करेगा"""
        while True:
            text = self.word_queue.get()
            if text is None: break

            try:
                # Turn ON UI animation
                try:
                    webview.windows[0].evaluate_js("assistantSpeaking(true)")
                except:
                    pass

                # हर वाक्य के लिए इंजन को रिफ्रेश करना सबसे सुरक्षित तरीका है
                engine = pyttsx3.init('sapi5')
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[0].id) # Index 0 for Male voice
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)

                print(f"\033[94mVasu-AI is speaking: {text}\033[0m")
                
                engine.say(text)
                engine.runAndWait()
                
                # इंजन को साफ़ सुथरा बंद करें
                engine.stop()
                del engine 
                
                # Turn OFF UI animation
                try:
                    webview.windows[0].evaluate_js("assistantSpeaking(false)")
                except:
                    pass

                # वाक्यों के बीच छोटा सा गैप (0.2 सेकंड) ताकि Windows ऑडियो बफर न फँसे
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Voice Error: {e}")
            
            finally:
                self.word_queue.task_done()

    def speak(self, text):
        """बिना डरे कितनी भी बार कॉल करें"""
        self.word_queue.put(text)

# Global Instance
assistant = VasuVoice()

def speak(text, rate="20%"): # rate parameter kept just to maintain compatibility if used elsewhere
    assistant.speak(text)


# ---------------- Folder fetch function  ----------------

def find_and_open(name):
    """
    Searches for any folder or file inside SEARCH_FOLDERS matching 'name'.
    Opens it automatically if found.
    """
    name = name.lower()

    for folder in SEARCH_FOLDERS:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            # Check folders
            for d in dirs:
                if name in d.lower():
                    path = os.path.join(root, d)
                    open_path(path)
                    return True

            # Check files
            for f in files:
                if name in f.lower():
                    path = os.path.join(root, f)
                    open_path(path)
                    return True

    return False

def open_path(path):
    """Open a file or folder depending on the OS"""
    if os.name == "nt":  # Windows
        os.startfile(path)
    else:
        subprocess.call(["xdg-open", path])


# ---------------- SPEECH ----------------
r = sr.Recognizer()

def process_command(command):
    command = command.lower()

    # SYSTEM COMMANDS
    if "open youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
        return

    if "open google" in command:
        webbrowser.open("https://google.com")
        speak("Opening Google")
        return
    
    if "whatsapp" in command:
        result = vasu_intent_engine(command)
        
        # Step 3: The Dispatcher checks the intent and calls the Action
        if result and result.get("intent") == "whatsapp":
            name = result.get("name")
            msg = result.get("message")
            # Step 4: Perform the action
            send_whatsapp_action(name, msg)
        else:
            print("AI could not understand the intent.")
        return

    if "shutdown" in command:
        speak("Are you sure you want to shut down? Say yes to confirm.")
        # asyncio.run(speak("Are you sure you want to shut down? Say yes to confirm."))


        try:
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=5)
                confirm = r.recognize_google(audio).lower()

            if "yes" in confirm:
                speak("Shutting down now")
                os.system("shutdown /s /t 5")
            else:
                speak("Shutdown cancelled")
        except Exception:
            speak("No confirmation received. Shutdown cancelled")
        return

    # ---------------- fetch and open ----------------
    if command.startswith(("open", "play")):
        # Remove keywords
        target_name = command
        for kw in ("open", "play"):
            target_name = target_name.replace(kw, "").strip()

        if not target_name:
            speak("Please say the file or folder name")
            return

        speak(f"Searching for {target_name}")

        found = find_and_open(target_name)

        if found:
            speak("Opening")
        else:
            speak("File or folder not found")

        return

    # NLP BRAIN
    print(f"Vasu-AI Brain is thinking...")
    answer = get_llm_response(command)
    
    # Step 2: Speak the answer
    if answer:
        print(f"Vasu-AI: {answer}")
        speak(answer)
    else:
        speak("I encountered an error in my thought process.")


# ---------------- MAIN LOOP ----------------
def start_assistant():
    global ACTIVE_SESSION   # 🔥 FIX
    speak("Welcome Back Sir")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=4)

            word = r.recognize_google(audio).lower()
            print("Heard:", word)

            # 🔐 WAKE WORD
            if not ACTIVE_SESSION:
                if "vasu" in word:
                    ACTIVE_SESSION = True
                    last_command_time = time.time()
                    speak("Welcome back sir, How can I help you today")
                continue

            # 💤 SLEEP COMMAND
            if "sleep" in word or "go to sleep" in word:
                ACTIVE_SESSION = False
                speak("Going to sleep")
                continue

            # 🎯 PROCESS COMMAND DIRECTLY
            last_command_time = time.time()
            process_command(word)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    # start assistant in background
    threading.Thread(target=start_assistant, daemon=True).start()

    # open HTML UI
    webview.create_window(
        "VASU Assistant",
        "Vasu_UI.html",   # path to your UI file
        width=1280,
        height=720
    )
    webview.start()