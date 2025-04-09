import json
from ollama import chat
from ollama import ChatResponse
import sqlite3
from datetime import datetime
def put_in_template(message):
    return f"You are a crypto trader. What is sentiment of following message's sentiment:\n{message}\nOutput in json format with 'sentiment', 'symbol', 'timespan' fields."

def process_messages ():
    with open('messages.json', 'r+') as f:
        chat = json.load(f)
        for item in chat["messages"]:
            text = "".join(entity["text"] for entity in item["text_entities"])
            if len(text) < 6: continue
            messages = {
                "timestamp": item["date"],
                "text": put_in_template(text)
            }
    return messages

def save_to_db(original_text, llm_prompt, llm_response, timestamp):
    conn = sqlite3.connect('crypto_sentiment.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sentiment_analysis 
        (original_text, llm_prompt, llm_response, timestamp, processed_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (original_text, llm_prompt, llm_response, timestamp, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def send_to_llm(message):
    response: ChatResponse = chat(model='deepseek-r1', messages=[
    {
        'role': 'user',
        'content': message["text"],
    },
    ])
    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)

def init_db():
    conn = sqlite3.connect('crypto_sentiment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT,
            llm_prompt TEXT,
            llm_response TEXT,
            timestamp TEXT,
            processed_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    init_db()  # Initialize database
    messages = process_messages()
    for item in messages:
        send_to_llm(item)
    