from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

# ➕ Реєстрація користувача
async def register_user(db: AsyncIOMotorDatabase, username: str, password: str):
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

# 🔑 Авторизація користувача
async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str):
    user = await db.users.find_one({"username": username, "password": password})
    if not user:
        return None

    # Оновити last_seen
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_seen": datetime.utcnow()}}
    )

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user")
    }


async def register_user(db: AsyncIOMotorDatabase, username: str, password: str):
    existing = await db.users.find_one({"username": username})
    if existing:
        print(f"Користувач {username} вже існує")
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
    print(f"Додано користувача: {username} з id {result.inserted_id}")
    user_data["_id"] = result.inserted_id

    return {
        "id": str(user_data["_id"]),
        "username": user_data["username"],
        "role": user_data["role"]
    }
