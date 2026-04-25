import speech_recognition as sr
import asyncio
import edge_tts
from playsound import playsound
import os
import pyautogui
import webbrowser
import subprocess
import time
import webview
import threading
from skills.whats_app import vasu_intent_engine, send_whatsapp_action

from brain import get_llm_response
USER_HOME = os.path.expanduser("~")

ACTIVE_SESSION=False
# SESSION_TIMOUT=False
# last_command_time=0



# List of folders your assistant should search
SEARCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Videos"),
]



# ---------------- SPEAK ----------------

async def speak(text , rate="20%"):
    try:
        webview.windows[0].evaluate_js("assistantSpeaking(true)")
    except:
        pass

    # voice = "en-AU-WilliamNeural"  # male voice
    voice = "hi-IN-SwaraNeural"  # female voice
    file = "voice.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file)
    playsound(file)
    os.remove(file)
    
    try:
       webview.windows[0].evaluate_js("assistantSpeaking(false)")
    except:
       pass

# # ---------------- LOAD BRAIN ----------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_PATH = os.path.join(BASE_DIR, "Data", "brain_data", "data.txt")

# dataset = load_qa_data(DATA_PATH)
# vectorizer, X = train_vectorizer(dataset)

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
        asyncio.run(speak("Opening YouTube"))
        return

    if "open google" in command:
        webbrowser.open("https://google.com")
        asyncio.run(speak("Opening Google"))
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
       asyncio.run(speak("Are you sure you want to shut down? Say yes to confirm."))

       try:
           with sr.Microphone() as source:
              audio = r.listen(source, timeout=5)
              confirm = r.recognize_google(audio).lower()

           if "yes" in confirm:
              asyncio.run(speak("Shutting down now"))
              os.system("shutdown /s /t 5")
            #   print("DEBUG: Shutdown command triggered")

           else:
              asyncio.run(speak("Shutdown cancelled"))
       except Exception:
            asyncio.run(speak("No confirmation received. Shutdown cancelled"))
       return
    # ---------------- fetech and open ----------------
    if command.startswith(("open", "play")):
    # Remove keywords
       target_name = command
       for kw in ("open", "play"):
          target_name = target_name.replace(kw, "").strip()

       if not target_name:
          asyncio.run(speak("Please say the file or folder name"))
          return

       asyncio.run(speak(f"Searching for {target_name}"))

       found = find_and_open(target_name)

       if found:
          asyncio.run(speak("Opening"))
       else:
          asyncio.run(speak("File or folder not found"))

       return

    # NLP BRAIN
    print(f"Vasu-AI Brain is thinking...")
    answer = get_llm_response(command)
   # Step 2: Speak the answer
    if answer:
      print(f"Vasu-AI: {answer}")
      asyncio.run(speak(answer))
    else:
      asyncio.run(speak("I encountered an error in my thought process."))

# ---------------- MAIN LOOP ----------------
def start_assistant():
  global ACTIVE_SESSION   # 🔥 FIX
  asyncio.run(speak("Welcome Back Sir "))

  while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=4)

        word = r.recognize_google(audio).lower()
        print("Heard:", word)

    #     if word == "vasu":
    #         asyncio.run(speak("Yes sir"))
    #         with sr.Microphone() as source:
    #             audio = r.listen(source)
    #         command = r.recognize_google(audio)
    #         print("Command:", command)
    #         process_command(command)

    # except Exception as e:
    #     print("Error:", e)
          # 🔐 WAKE WORD
        if not ACTIVE_SESSION:
            if "vasu" in word:
                ACTIVE_SESSION = True
                last_command_time = time.time()
                asyncio.run(speak("welcome back sir , How can I help you today"))
            continue

        # 💤 SLEEP COMMAND
        if "sleep" in word or "go to sleep" in word:
            ACTIVE_SESSION = False
            asyncio.run(speak("Going to sleep"))
            continue

        # # ⏳ AUTO SLEEP AFTER TIMEOUT
        # if time.time() - last_command_time > SESSION_TIMOUT:
        #     ACTIVE_SESSION = False
        #     asyncio.run(speak("Session expired. Say Vasu to wake me up"))
        #     continue

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