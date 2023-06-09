import requests

from app.config import API_KEY

MODEL = 'gpt-3.5-turbo'
URL = f"https://api.openai.com/v1/chat/completions"
MAX_TOKENS = 2000


def chat_with_chatgpt(prompt=''):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    json_payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
    }
    res = requests.post(URL, headers=headers, json=json_payload).json()
    if "error" in res:
        return res["error"]['message']
    return res['choices'][0]['message']['content']


def tweet(length : str = 20) -> str:
    prompt = f"""
    Tweet a {length} words, random, make sense and do NOT be the same as the previous one.
    """
    text = chat_with_chatgpt(prompt)
    if "That model is currently overloaded with other requests" in text:
        return "I just found a lucky penny in the street and I feel like today is going to be a great day! #blessed"
    return text
