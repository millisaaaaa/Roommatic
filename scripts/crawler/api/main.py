from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import json

from scripts.crawler.search_catalog import search_appliances_in_catalog
from scripts.crawler.find_catalog import find_appliance_in_catalog
from scripts.crawler.search_appliance import search_appliance_online
from scripts.crawler.save_catalog import save_appliance_to_catalog
from scripts.crawler.save_room_appliance import save_room_appliance
from scripts.crawler.list_room_appliances import list_room_appliances

app = FastAPI()
load_dotenv("/home/pi/Roommatic/.env")

client = OpenAI()


class RoomieRequest(BaseModel):
    message: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RoomApplianceCreate(BaseModel):
    room_id: int
    appliance_id: int | None = None
    appliance_name: str
    quantity: int = 1
    custom_power: float | None = None
    control_method: str = "none"

@app.get("/")
def root():
    return {"message": "Roommatic API running"}

@app.get("/appliances/search")
def search_appliance(category: str | None = None, brand: str | None = None, model: str | None = None):
    # 先做字典模糊搜尋
    results = search_appliances_in_catalog(category=category, brand=brand, model=model, limit=20)

    if results:
        return {
            "status": "found_in_db",
            "count": len(results),
            "data": results
        }

    # 若完全沒有結果，且三個欄位都有填，才嘗試單筆補抓
    if category and brand and model:
        result = search_appliance_online(brand, model, category)

        if result:
            save_appliance_to_catalog(result)

            return {
                "status": "fetched_and_saved",
                "count": 1,
                "data": [result]
            }

    return {
        "status": "not_found",
        "count": 0,
        "data": []
    }

@app.post("/room_appliances")
def create_room_appliance(payload: RoomApplianceCreate):
    try:
        room_appliance_id = save_room_appliance(payload.dict())

        return {
            "status": "created",
            "room_appliance_id": room_appliance_id,
            "data": payload.dict()
        }
    except Exception as e:
        print("create_room_appliance error:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/room_appliances")
def get_room_appliances(room_id: int):
    try:
        results = list_room_appliances(room_id)
        return {
            "status": "ok",
            "count": len(results),
            "data": results
        }
    except Exception as e:
        print("get_room_appliances error:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))
    
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