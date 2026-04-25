 #this whole is prototyle function and logic to fetch and open file
"""
import os
import subprocess
from brain import load_qa_data, train_vectorizer, get_answer
USER_HOME = os.path.expanduser("~")

SEARCH_FOLDERS = [
    os.path.join(USER_HOME, "Desktop"),
    os.path.join(USER_HOME, "Documents"),
    os.path.join(USER_HOME, "Downloads"),
    os.path.join(USER_HOME, "Pictures"),              # ✅ IMPORTANT        
    os.path.join(USER_HOME, "Pictures", "Saved Pictures"),
    os.path.join(USER_HOME, "OneDrive"),
    os.path.join(USER_HOME, "OneDrive", "Pictures"),
    os.path.join(USER_HOME, "OneDrive", "Documents"),
    os.path.join(USER_HOME, "OneDrive", "Desktop"),
    os.path.join(USER_HOME,"Video","Movies","Harry Potter")
]


def find_and_open(name):                                    
    name = name.lower()

    for folder in SEARCH_FOLDERS:
        for root, dirs, files in os.walk(folder):

            # 🔹 CHECK FOLDERS
            for d in dirs:
                if name in d.lower():
                    path = os.path.join(root, d)
                    open_path(path)
                    return True

            # 🔹 CHECK FILES
            for f in files:
                if name in f.lower():
                    path = os.path.join(root, f)
                    open_path(path)
                    return True

    return False


def open_path(path):
    if os.name == "nt":  # Windows
        os.startfile(path)
    else:
        subprocess.call(["xdg-open", path])
"""



# def find_file(filename):
#     for folder in SEARCH_FOLDERS:
#         for root, _, files in os.walk(folder):
#             for name in files:
#                 if filename.lower() in name.lower():
#                     return os.path.join(root, name)
#     return None



# This the prototype calling condition to fetch and open file 
"""
 if command.startswith(("open", "play")):
    #    filename = command.replace("open", "").strip()
       filename = command
       for kw in ("open", "play"):
            filename = filename.replace(kw, "").strip()


       if not filename:
          asyncio.run(speak("Please say the file name"))
          return

       asyncio.run(speak(f"Searching for {filename}"))

       file_path = find_and_open(filename)

       if file_path:
        os.startfile(file_path)
        asyncio.run(speak("Opening file"))
       else:
        asyncio.run(speak("File not found"))
       found = find_and_open(filename)

       if found:
        asyncio.run(speak("Opening"))
       else:
        asyncio.run(speak("File or folder not found"))

       return

"""


# def open_whatsapp():
#     chrome_paths = [
#         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
#     ]

#     chrome = next((p for p in chrome_paths if os.path.exists(p)), None)

#     if chrome:
#         subprocess.Popen([chrome, "--new-window", "https://web.whatsapp.com"])
#     else:
#         import webbrowser
#         webbrowser.open("https://web.whatsapp.com")

#     time.sleep(10)  # allow WhatsApp to load

# def send_message(contact, message):
#     open_whatsapp()

#     # Click search bar (adjust if needed)
#     pyautogui.click(500, 500)
#     time.sleep(1)
#  # Open search
#     pyautogui.hotkey("ctrl", "alt", "/")
#     time.sleep(1)

#     pyautogui.write(contact, interval=0.1)
#     time.sleep(2)
#     pyautogui.press("enter")

#     time.sleep(1)
#     pyautogui.write(message, interval=0.05)
#     pyautogui.press("enter")
# contact 





# def process_whatsapp_command(command):
#     """
#     Example command:
#     "Send a Hi to Papa on WhatsApp"
#     """
#     command = command.lower()

    # # Check if it contains WhatsApp keyword
    # if "whatsapp" not in command:
    #     return False

    # try:
    #     # Extract message and contact name
    #     # Assumes format: send [message] to [contact] on whatsapp
    #     msg_part = command.split("send")[1].split("to")[0].strip()
    #     contact_part = command.split("to")[1].split("on whatsapp")[0].strip()

    #     message = msg_part
    #     contact_name = contact_part

    #     if contact_name not in contacts:
    #         asyncio.run(speak(f"I did not find {contact_name} in your contacts"))
    #         return True

    #     phone_number = contacts[contact_name]
    #     send_message_number(phone_number, message)
    #     asyncio.run(speak(f"Message sent to {contact_name}"))

    # except Exception as e:
    #     print("Error parsing WhatsApp command:", e)
    #     asyncio.run(speak("Sorry, I could not understand the command"))

    # return True