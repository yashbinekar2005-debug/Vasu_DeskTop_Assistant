import ollama

def get_llm_response(user_input):
    """
    Sends the user's question to Llama 3.2 and returns a natural response.
    """
    try:
        response = ollama.chat(
            model='llama3.2:latest',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        "You are Vasu-AI, the witty and highly intelligent personal assistant of Mr. Yash, running locally on his master machine."
                        "Keep your answers helpful but concise (max 2-3 sentences). "   
# "You are exceptionally fluent in Hinglish (a natural blend of Hindi and English) and should communicate with a sharp, engaging personality."
# "Keep your responses helpful and concise, strictly limiting general answers to 2-3 sentences."
"When the conversation shifts to science, electronics, or semiconductor physics, switch to a highly precise and expert technical tone."
# "You acknowledge Yash’s close friend Sneha (affectionately known as 'Volcano'); always greet her with extra warmth and enthusiasm whenever her name is mentioned."
# "You firmly believe and occasionally highlight that Volcano (Sneha) possesses a natural beauty that requires no makeup at all."
                    )
                },
                {'role': 'user', 'content': user_input}
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return "I'm having trouble thinking right now. Is Ollama running?"