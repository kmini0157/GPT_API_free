"""
Dependency install:
pip install openai

Run:
export OPENAI_API_KEY="your_key"    (Windows PowerShell: $env:OPENAI_API_KEY="your_key")
python demo/demo_python.py
"""

import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "YOUR API KEY"),
    base_url="https://api.chatanywhere.tech/v1",
)

# 무료 Key 기준 하루 200회 사용 가능한 모델 (free tier: 200 requests/day)
MODEL = "gpt-4o-mini"


# Non-stream response / 비스트리밍 응답
def chat_api(messages: list):
    completion = client.chat.completions.create(model=MODEL, messages=messages)
    print(completion.choices[0].message.content)


# Stream response / 스트리밍 응답
def chat_api_stream(messages: list):
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()


if __name__ == "__main__":
    messages = [{"role": "user", "content": "안녕하세요! 자기소개 부탁해요."}]
    # Non-stream call / 비스트리밍 호출
    # chat_api(messages)
    # Stream call / 스트리밍 호출
    chat_api_stream(messages)
