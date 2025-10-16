import requests
from flask import current_app

def call_groq_ai(prompt, system_message="You are a helpful business advisor."):
    headers = {
        "Authorization": f"Bearer {current_app.config['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if 'choices' in result and result['choices']:
            return result['choices'][0]['message']['content']
        else:
            return f"Groq API Error: Unexpected response format\n{result}"
    except requests.exceptions.RequestException as e:
        return f"HTTP error from Groq API: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


