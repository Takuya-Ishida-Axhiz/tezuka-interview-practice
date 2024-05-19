import json
import os
import hashlib
from fastapi import FastAPI, Request
from dto.ChatDto import ChatRequest
import openai

from dotenv import load_dotenv

# .envファイルの内容を読み込見込む
load_dotenv()

app = FastAPI()
# 環境変数から読み込み
print(os.environ["OPENAI_API_KEY"])
openai.api_key = os.environ["OPENAI_API_KEY"]


@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_history_filename(user_agent: str) -> str:
    print("get_history_filename")
    # ユーザーエージェントをハッシュ化してファイル名を生成
    hash_object = hashlib.sha256(user_agent.encode())
    return f"conversation_history_{hash_object.hexdigest()}.json"


def load_history(user_agent: str):
    filename = get_history_filename(user_agent)
    print("load_history")
    print(filename)
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_history(user_agent: str, history):
    print("save_history")
    filename = get_history_filename(user_agent)
    print(filename)
    with open(filename, "w") as file:
        json.dump(history, file)


@app.post("/chat")
def chat(request: Request, chat_request: ChatRequest) -> dict[str, str]:
    user_agent = request.headers.get("user-agent")
    input_text = chat_request.input
    print("chat")
    print(user_agent)
    print(input_text)

    messages = load_history(user_agent)
    messages.append({"role": "user", "content": input_text})

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        temperature=0,
    )

    response_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": response_message})
    print(messages)

    save_history(user_agent, messages)

    return {"response": response_message}
