from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

app = FastAPI()

app.mount("/image", StaticFiles(directory="D:/Sport/image"), name="image")
# Монтуємо статичну папку з картинками
app.mount("/image", StaticFiles(directory="image"), name="image")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ти можеш обмежити фронтенд тут
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb+srv://ilabudko843:IuIqSzif0dmykady@cluster0.lftu1nd.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_URI)
db = client['gymdb']  # Вказати ім'я твоєї бази

# Pydantic моделі

class UserIn(BaseModel):
    username: str
    password: str

class SaveResultRequest(BaseModel):
    user_id: str  # string, оскільки MongoDB ObjectId
    exercise: str
    value: int

class UpdateUsernameRequest(BaseModel):
    username: str

# Реєстрація користувача
@app.post("/register")
async def register(user: UserIn):
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    role = "admin" if user.username == "mersiliess" and user.password == "bog" else "user"
    user_doc = {
        "username": user.username,
        "password": user.password,
        "role": role,
        "created_at": datetime.utcnow(),
        "last_seen": datetime.utcnow()
    }
    res = await db.users.insert_one(user_doc)
    return {"msg": "registered", "user_id": str(res.inserted_id)}

# Авторизація
@app.post("/login")
async def login(user: UserIn):
    existing = await db.users.find_one({"username": user.username, "password": user.password})
    if not existing:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await db.users.update_one(
        {"_id": existing["_id"]},
        {"$set": {"last_seen": datetime.utcnow()}}
    )

    return {"user_id": str(existing["_id"]), "role": existing.get("role", "user")}

# Збереження результату
@app.post("/save_result")
async def save_result(data: SaveResultRequest):
    user = await db.users.find_one({"_id": ObjectId(data.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result_doc = {
        "user_id": data.user_id,
        "exercise": data.exercise,
        "value": data.value,
        "date": datetime.utcnow()
    }
    res = await db.results.insert_one(result_doc)
    return {"msg": "saved", "result_id": str(res.inserted_id)}

# Отримати всі результати користувача
@app.get("/results/{user_id}")
async def get_results(user_id: str):
    cursor = db.results.find({"user_id": user_id})
    results = []
    async for r in cursor:
        results.append({
            "exercise": r["exercise"],
            "value": r["value"],
            "date": r["date"]
        })
    return results

# Отримати список усіх користувачів
@app.get("/users")
async def get_all_users():
    cursor = db.users.find()
    users = []
    async for u in cursor:
        users.append({
            "id": str(u["_id"]),
            "username": u["username"],
            "role": u.get("role", "user")
        })
    return users

# Головна сторінка
@app.get("/")
async def root():
    return {"message": "🔥 Fitness backend is running!"}

# Ти можеш дописати адміністраторські ендпоінти аналогічно — через MongoDB методи.

