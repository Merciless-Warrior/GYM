from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app_models import Base, User, WorkoutResult, SessionLocal, engine
from backend.auth_module import register_user, authenticate_user
from backend.workouts_data import add_workout_result, get_user_results
import shutil
from datetime import datetime

app = FastAPI()

# Монтуємо статичну папку з картинками
app.mount("/image", StaticFiles(directory="D:/Sport/image"), name="image")

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Створення таблиць
Base.metadata.create_all(bind=engine)

# Резервне копіювання бази при запуску
@app.on_event("startup")
def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy("db.sqlite3", f"backup_{timestamp}.sqlite3")

# Залежність для сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Моделі запитів
class UserIn(BaseModel):
    username: str
    password: str

class SaveResultRequest(BaseModel):
    user_id: int
    exercise: str
    value: int

class UpdateUsernameRequest(BaseModel):
    username: str

# Реєстрація користувача
@app.post("/register")
def register(user: UserIn, db: Session = Depends(get_db)):
    try:
        new_user = register_user(db, user.username, user.password)
        if not new_user:
            raise HTTPException(status_code=400, detail="User already exists")
        return {"msg": "registered", "user_id": new_user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# Авторизація
@app.post("/login")
def login(user: UserIn, db: Session = Depends(get_db)):
    existing_user = authenticate_user(db, user.username, user.password)
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": existing_user.id, "role": existing_user.role}

# Збереження результату
@app.post("/save_result")
def save_result(data: SaveResultRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        result = add_workout_result(db, data.user_id, data.exercise, data.value)
        return {"msg": "saved", "result_id": result.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# Отримати всі результати користувача
@app.get("/results/{user_id}")
def get_results(user_id: int, db: Session = Depends(get_db)):
    results = get_user_results(db, user_id)
    return [{"exercise": r.exercise, "value": r.value, "date": r.date} for r in results]

# Отримати список усіх користувачів
@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username} for u in users]

# Головна сторінка
@app.get("/")
def root():
    return {"message": "🔥 Fitness backend is running!"}

# Статистика по користувачу (тільки для адміна)
@app.get("/admin/user_stats/{user_id}")
def get_user_stats(user_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)):
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    results = get_user_results(db, user_id)
    return {
        "username": user.username,
        "results": [{"exercise": r.exercise, "value": r.value, "date": r.date} for r in results]
    }

# Отримати всіх користувачів для адміна
@app.get("/admin/users")
def admin_users(admin_id: int = Query(...), db: Session = Depends(get_db)):
    admin = db.query(User).filter_by(id=admin_id).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]

# Призначити користувача адміністратором
@app.post("/make_admin/{user_id}")
def make_admin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "admin"
    try:
        db.commit()
        return {"msg": f"{user.username} is now admin"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# Видалення користувача (тільки адміністратор)
@app.delete("/admin/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(user_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)):
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"msg": f"User {user.username} deleted"}

# Оновлення імені користувача
@app.put("/update_username/{user_id}")
def update_username(user_id: int, req: UpdateUsernameRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = req.username
    try:
        db.commit()
        return {"msg": "Username updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
