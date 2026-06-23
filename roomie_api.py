from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv("/home/pi/Roommatic/.env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

class RoomieRequest(BaseModel):
    message: str

@app.post("/roomie")
def roomie(req: RoomieRequest):
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": (
                    "你是 Roomie，是 Roommatic 智慧節能空間管理系統的可愛助理。"
                    "請用活潑、親切、簡短的繁體中文回答。"
                    "你的輸出一定要是 JSON 格式，只有 paragraph 這個欄位。"
                )
            },
            {
                "role": "user",
                "content": req.message
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "response_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "paragraph": {"type": "string"}
                    },
                    "required": ["paragraph"],
                    "additionalProperties": False
                }
            }
        }
    )

    text = response.output_text
    data = json.loads(text)

    return data