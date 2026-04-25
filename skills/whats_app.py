import ollama
import json
import os 
import pyautogui
import time
from urllib.parse import quote  # Important for URL formatting
import difflib

# 1. Your Contacts
contacts = {
    "papa": "+919823157270",
    "zandu": "+919322529194",
    "jay": "+917030535844",
    "Sonu Tai":"+91 95423 62352",
    "Rakshit":"+91 7058490453"
}

def vasu_intent_engine(user_input):
    """Uses Llama 3.2 to extract the Name and Message."""
    try:
        response = ollama.chat(
            model='llama3.2:latest', 
            messages=[
                {
                    'role': 'system', 
                    'content': (
    (
                        "You are Vasu-AI's core intent engine. "
                        "Your goal: Extract 'name' and 'message'. "
                        "RULES: "
                        "1. If the message is 'hi', 'ok', 'hello', or any single word, you MUST extract it. "
                        "2. Do not include 'Vasu' or 'WhatsApp' in the name or message fields. "
                        "3. Ignore filler words like 'please', 'tell', 'send'. "
                        "4. OUTPUT FORMAT: Respond ONLY with valid JSON: "
                        "{'intent': 'whatsapp', 'name': 'target_person', 'message': 'text_content'}"
                    )
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

# def send_whatsapp_action(extracted_name, message):
#     """
#     Fuzzy Logic: Matches 'Sonu' to 'Sonu Tai' automatically.
#     """
#     # Look for the best match in your contact keys
#     matches = difflib.get_close_matches(extracted_name.lower(), contacts.keys(), n=1, cutoff=0.5)
#     """Opens the Desktop App and sends the message."""
#     # Standardize name to match dictionary keys
#     target_name =extracted_name.lower().strip()
#     phone = contacts.get(target_name)
    
#     if phone:
#         # Encode message for the URL (replaces spaces with %20)
#         encoded_message = quote(message)
#         whatsapp_url = f"whatsapp://send?phone={phone}&text={encoded_message}"
        
#         print(f"Vasu-AI: Opening WhatsApp Desktop for {target_name}...")
#         os.startfile(whatsapp_url) 
        
#         # Wait for the app to focus
#         time.sleep(6) 
        
#         # Press Enter to send
#         pyautogui.press('enter')
#         print("Vasu-AI: Message sent!")
#         return True
#     else:
#         print(f"Error: {target_name} not found in contacts.")
#         return False

def send_whatsapp_action(extracted_name, message):
    """
    Standardizes everything to lowercase so 'SONU' matches 'Sonu Tai'.
    """
    # Create a mapping of lowercase names to original names/numbers
    # This ensures 'sonu tai' (lower) points to the correct entry
    norm_contacts = {k.lower(): (k, v) for k, v in contacts.items()}
    
    # Convert what the AI heard to lowercase for a fair comparison
    search_name = extracted_name.lower().strip()
    
    # Fuzzy match against the lowercase keys
    matches = difflib.get_close_matches(search_name, norm_contacts.keys(), n=1, cutoff=0.4)
    
    if matches:
        best_match_lower = matches[0]
        original_name, phone = norm_contacts[best_match_lower]
        
        # Prepare the App URL
        encoded_msg = quote(message)
        # This protocol opens the Windows App directly
        whatsapp_url = f"whatsapp://send?phone={phone}&text={encoded_msg}"
        
        print(f"Vasu-AI: Fuzzy Match! '{extracted_name}' -> '{original_name}'")
        
        # Launch the Desktop App
        os.startfile(whatsapp_url)
        
        # Wait for the app to focus (usually faster than web, 6-8s is safe)
        time.sleep(7) 
        
        # Press Enter to send
        pyautogui.press('enter')
        print(f"Vasu-AI: Message sent to {original_name} via Desktop App.")
        return True
    else:
        print(f"Vasu-AI: Could not find '{extracted_name}' in your contacts.")
        return False