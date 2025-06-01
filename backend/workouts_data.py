from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

# ➕ Додати результат
async def add_workout_result(db: AsyncIOMotorDatabase, user_id: str, exercise: str, value: int):
    result = {
        "user_id": user_id,
        "exercise": exercise,
        "value": value,
        "date": datetime.utcnow()
    }
    r = await db.results.insert_one(result)
    result["_id"] = r.inserted_id
    return result

# 📄 Отримати всі результати користувача
async def get_user_results(db: AsyncIOMotorDatabase, user_id: str):
    cursor = db.results.find({"user_id": user_id})
    results = []
    async for r in cursor:
        results.append(r)
    return results