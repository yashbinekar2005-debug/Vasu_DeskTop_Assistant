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
from skills.whats_app import vasu_intent_engine, send_whatsapp_action
from brain import get_llm_response


USER_HOME = os.path.expanduser("~")
ACTIVE_SESSION = False

SEARCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Videos"),
]

# ─────────────────────────────────────────────────────────
#  UI BRIDGE — all calls to the frontend go through here
# ─────────────────────────────────────────────────────────

def ui(js: str):
    """Safely fire JS on the webview window. Silently ignores if window not ready."""
    try:
        webview.windows[0].evaluate_js(js)
    except Exception as e:
        print(f"[UI] JS call failed: {e}")


def ui_speaking(state: bool):
    """Trigger lip sync + waveform animation. Matches assistantSpeaking() in HTML."""
    ui(f"assistantSpeaking({'true' if state else 'false'})")


def ui_show_response(text: str, emotion: str = "neutral"):
    """
    Show typewriter text in speech bubble + right panel.
    emotion: 'neutral' | 'happy' | 'sad' | 'angry' | 'excited'
    """
    # Escape single quotes so JS string doesn't break
    safe_text  = text.replace("'", "\\'").replace("\n", " ")
    safe_emo   = emotion if emotion in ('neutral','happy','sad','angry','excited') else 'neutral'
    ui(f"showResponse('{safe_text}', '{safe_emo}')")


def ui_set_listening(state: bool):
    """Show/hide the pulsing listen ring around the avatar."""
    ui(f"setListening({'true' if state else 'false'})")


def ui_set_wake(state: bool):
    """Show/hide the VASU ACTIVE badge and update mode label."""
    ui(f"setWakeState({'true' if state else 'false'})")


def ui_log(msg: str):
    """Push a line to the session log panel."""
    safe = msg.replace("'", "\\'")
    ui(f"addLogEntry('{safe}')")


def ui_set_emotion(name: str):
    """Directly change the avatar emotion color + face."""
    ui(f"setEmotion('{name}')")


# ─────────────────────────────────────────────────────────
#  SIMPLE SENTIMENT → EMOTION MAPPER
#  (Replace with your own NLP logic if desired)
# ─────────────────────────────────────────────────────────

def detect_emotion(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["sorry","couldn't","error","fail","unfortunate","unable"]):
        return "sad"
    if any(w in t for w in ["alert","warning","danger","stop","shutdown","critical"]):
        return "angry"
    if any(w in t for w in ["great","done","success","perfect","completed","excellent","sure"]):
        return "happy"
    if any(w in t for w in ["incredible","amazing","wow","unbelievable","fantastic"]):
        return "excited"
    return "neutral"


# ─────────────────────────────────────────────────────────
#  VOICE ENGINE (pyttsx3 — persistent background thread)
# ─────────────────────────────────────────────────────────

class VasuVoice:
    def __init__(self):
        self.word_queue = queue.Queue()
        self.rate   = 180
        self.volume = 1.0
        threading.Thread(target=self._speak_handler, daemon=True).start()

    def _speak_handler(self):
        while True:
            text = self.word_queue.get()
            if text is None:
                break
            try:
                # ── Tell UI: lips start moving ──
                ui_speaking(True)

                engine = pyttsx3.init('sapi5')
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[0].id)   # 0 = Male
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)

                print(f"\033[94mVasu-AI is speaking: {text}\033[0m")
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                del engine

                time.sleep(0.2)

            except Exception as e:
                print(f"Voice Error: {e}")
            finally:
                # ── Tell UI: lips stop moving ──
                ui_speaking(False)
                self.word_queue.task_done()

    def speak(self, text: str):
        self.word_queue.put(text)


assistant = VasuVoice()


def speak(text: str, emotion: str = None):
    """
    Speak text aloud AND push it to the UI bubble simultaneously.
    emotion: auto-detected from text if not provided.
    """
    emo = emotion or detect_emotion(text)
    # Show text + emotion on UI immediately (before audio starts)
    ui_show_response(text, emo)
    # Queue for TTS (will call ui_speaking true/false internally)
    assistant.speak(text)


# ─────────────────────────────────────────────────────────
#  FILE / FOLDER FINDER
# ─────────────────────────────────────────────────────────

def find_and_open(name: str) -> bool:
    name = name.lower()
    for folder in SEARCH_FOLDERS:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            for d in dirs:
                if name in d.lower():
                    open_path(os.path.join(root, d))
                    return True
            for f in files:
                if name in f.lower():
                    open_path(os.path.join(root, f))
                    return True
    return False


def open_path(path: str):
    if os.name == "nt":
        os.startfile(path)
    else:
        subprocess.call(["xdg-open", path])


# ─────────────────────────────────────────────────────────
#  COMMAND PROCESSOR
# ─────────────────────────────────────────────────────────

r = sr.Recognizer()


def process_command(command: str):
    command = command.lower()
    ui_log(f"Command: {command[:50]}")

    # ── SYSTEM COMMANDS ──
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
        if result and result.get("intent") == "whatsapp":
            name = result.get("name")
            msg  = result.get("message")
            send_whatsapp_action(name, msg)
            speak(f"Sending WhatsApp message to {name}")
        else:
            speak("I could not understand the WhatsApp command.")
        return

    if "shutdown" in command:
        speak("Are you sure you want to shut down? Say yes to confirm.")
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=5)
                confirm = r.recognize_google(audio).lower()
            if "yes" in confirm:
                speak("Shutting down now", emotion="angry")
                os.system("shutdown /s /t 5")
            else:
                speak("Shutdown cancelled")
        except Exception:
            speak("No confirmation received. Shutdown cancelled")
        return

    # ── FILE / FOLDER OPEN ──
    if command.startswith(("open", "play")):
        target_name = command
        for kw in ("open", "play"):
            target_name = target_name.replace(kw, "").strip()

        if not target_name:
            speak("Please say the file or folder name")
            return

        speak(f"Searching for {target_name}")
        if find_and_open(target_name):
            speak("Opening", emotion="happy")
        else:
            speak("File or folder not found", emotion="sad")
        return

    # ── LLM BRAIN ──
    ui_log("Brain is thinking...")
    ui_set_emotion("neutral")
    print("Vasu-AI Brain is thinking...")

    answer = get_llm_response(command)

    if answer:
        print(f"Vasu-AI: {answer}")
        speak(answer)   # emotion auto-detected from answer text
    else:
        speak("I encountered an error in my thought process.", emotion="sad")


# ─────────────────────────────────────────────────────────
#  MAIN LISTEN LOOP
# ─────────────────────────────────────────────────────────

def start_assistant():
    global ACTIVE_SESSION

    speak("Welcome Back Sir", emotion="happy")

    while True:
        try:
            # Show listening indicator
            ui_set_listening(True)

            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=4)

            # Mic done — hide ring
            ui_set_listening(False)

            word = r.recognize_google(audio).lower()
            print("Heard:", word)
            ui_log(f"Heard: {word[:50]}")

            # ── WAKE WORD ──
            if not ACTIVE_SESSION:
                if "vasu" in word:
                    ACTIVE_SESSION = True
                    ui_set_wake(True)
                    speak("Welcome back sir, how can I help you today", emotion="happy")
                continue

            # ── SLEEP COMMAND ──
            if "sleep" in word or "go to sleep" in word:
                ACTIVE_SESSION = False
                ui_set_wake(False)
                speak("Going to sleep")
                continue

            # ── PROCESS COMMAND ──
            process_command(word)

        except sr.WaitTimeoutError:
            # Normal silence — just keep listening
            ui_set_listening(False)

        except sr.UnknownValueError:
            # Didn't catch speech clearly
            ui_set_listening(False)

        except Exception as e:
            ui_set_listening(False)
            print("Error:", e)


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start assistant in background thread
    threading.Thread(target=start_assistant, daemon=True).start()

    # Launch pywebview with the UI
    webview.create_window(
        "VASU Assistant",
        "Vasu_UI.html",
        width=1280,
        height=720
    )
    webview.start()
