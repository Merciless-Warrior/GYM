from sqlalchemy.orm import Session
from backend.app_models import WorkoutResult

# ➕ Додати новий результат тренування
def add_workout_result(db: Session, user_id: int, exercise: str, value: int):
    if not user_id:
        raise ValueError("user_id обов’язковий для запису результату")
    result = WorkoutResult(user_id=user_id, exercise=exercise, value=value)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

# 📄 Отримати всі результати користувача
def get_user_results(db: Session, user_id: int):
    return db.query(WorkoutResult).filter_by(user_id=user_id).all()
