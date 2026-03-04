import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("--- 你可以使用的模型清單 ---")
try:
    for m in client.models.list():
        print(f"可用 ID: {m.name}")
except Exception as e:
    print(f"讀取清單失敗，可能是 API Key 權限問題: {e}")