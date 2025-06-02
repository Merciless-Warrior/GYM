from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict

MONGO_URI = "mongodb+srv://ilabudko843:IuIqSzif0dmykady@cluster0.lftu1nd.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "gymdb"

app = FastAPI()

app.mount("/image", StaticFiles(directory="D:/Sport/image"), name="image")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для локального тесту можна так, в проді краще вказати свої домени
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

class UserIn(BaseModel):
    username: str
    password: str

class SaveResultRequest(BaseModel):
    user_id: str
    exercise: str
    value: int

async def register_user(db: AsyncIOMotorDatabase, username: str, password: str) -> Optional[Dict]:
    existing = await db.users.find_one({"username": username})
    if existing:
        return None
    role = "admin" if username == "mersiliess" and password == "bog" else "user"
    user_data = {
        "username": username,
        "password": password,
        "role": role,
        "created_at": datetime.utcnow(),
        "last_seen": datetime.utcnow()
    }
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return {
        "id": str(user_data["_id"]),
        "username": user_data["username"],
        "role": user_data["role"]
    }

async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str) -> Optional[Dict]:
    user = await db.users.find_one({"username": username, "password": password})
    if not user:
        return None
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_seen": datetime.utcnow()}}
    )
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user")
    }

async def add_workout_result(db: AsyncIOMotorDatabase, user_id: str, exercise: str, value: int) -> Dict:
    result = {
        "user_id": user_id,
        "exercise": exercise,
        "value": value,
        "date": datetime.utcnow()
    }
    r = await db.results.insert_one(result)
    result["_id"] = r.inserted_id
    return result

async def get_user_results(db: AsyncIOMotorDatabase, user_id: str) -> List[Dict]:
    cursor = db.results.find({"user_id": user_id})
    results = []
    async for r in cursor:
        r["id"] = str(r["_id"])
        results.append(r)
    return results

@app.post("/register")
async def api_register(user: UserIn):
    registered = await register_user(db, user.username, user.password)
    if not registered:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"msg": "registered", "user_id": registered["id"]}

@app.post("/login")
async def api_login(user: UserIn):
    auth = await authenticate_user(db, user.username, user.password)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": auth["id"], "role": auth["role"]}

@app.post("/save_result")
async def api_save_result(data: SaveResultRequest):
    try:
        user_obj_id = ObjectId(data.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await add_workout_result(db, data.user_id, data.exercise, data.value)
    return {"msg": "saved", "result_id": str(result["_id"])}

@app.get("/results/{user_id}")
async def api_get_results(user_id: str):
    results = await get_user_results(db, user_id)
    return results

@app.get("/users")
async def api_get_all_users():
    cursor = db.users.find()
    users = []
    async for u in cursor:
        users.append({
            "id": str(u["_id"]),
            "username": u["username"],
            "role": u.get("role", "user")
        })
    return users

@app.get("/")
async def root():
    return {"message": "🔥 Fitness backend is running!"}
