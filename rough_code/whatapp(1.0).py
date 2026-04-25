import ollama
import json
import pywhatkit
import pyautogui
import time

# 1. Your Contacts (Ensure they have country codes for pywhatkit)
contacts = {
    "papa": "+919823157270",
    "yug": "+919322529194",
    "jay": "+917030535844"
}

def vasu_intent_engine(user_input):
    """
    Uses Llama 3.2 to extract the Name and Message from your voice command.
    """
    try:
        response = ollama.chat(
            model='llama3.2:latest', 
            messages=[
                {
                    'role': 'system', 
                    'content': (
    "You are Vasu-AI. The user will call you 'Vasu'. "
    "NEVER extract 'Vasu' as the target name. "
    "Extract the 'name' of the PERSON the user wants to talk to and the 'message'. "
    "Respond ONLY in JSON format: {'intent': 'whatsapp', 'name': 'target_person', 'message': 'text'}"
)
                },
                {'role': 'user', 'content': user_input}
            ],
            format='json'
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Llama Error: {e}")
        return None

def send_whatsapp_action(name, message):
    """
    Physically opens the browser and sends the message.
    """
    try:
        phone = contacts.get(name.lower())
        if phone:
            print(f"Action: Sending '{message}' to {name} ({phone})")
            # Opens browser, waits 15 seconds for load, then types message
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=False)
            
            # Small delay to ensure text is typed
            time.sleep(3) 
            
            # Press 'Enter' to send
            pyautogui.press('enter')
            print("Done!")
        else:
            print(f"Error: '{name}' is not in your contacts list.")
    except Exception as e:
        print(f"Automation Error: {e}")

# --- EXECUTION FLOW ---

# Step 1: The Voice Command
command = "Hey Vasu, tell Jay I will be there in 5 minutes on WhatsApp"

# Step 2: The Brain (Llama 3.2) parses the command
result = vasu_intent_engine(command)

# Step 3: The Dispatcher checks the intent and calls the Action
if result and result.get("intent") == "whatsapp":
    name = result.get("name")
    msg = result.get("message")
    
    # Step 4: Perform the action
    send_whatsapp_action(name, msg)
else:
    print("AI could not understand the intent.")