import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = "mongodb+srv://ilabudko843:IuIqSzif0dmykady@cluster0.lftu1nd.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "gymdb"

async def safe_add_fields():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    cursor = db.users.find({})
    updated_count = 0

    async for user in cursor:
        updates = {}
        if 'created_at' not in user:
            updates['created_at'] = datetime.utcnow()
        if 'last_seen' not in user:
            updates['last_seen'] = datetime.utcnow()

        if updates:
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": updates}
            )
            updated_count += 1

    print(f"✅ Оновлено користувачів: {updated_count}")

if __name__ == "__main__":
    asyncio.run(safe_add_fields())
