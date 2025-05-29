from sqlalchemy.orm import Session
from backend.app_models import User

def register_user(db: Session, username: str, password: str):
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        return None

    # Якщо логін і пароль співпадають — це адмін
    role = "admin" if username == "mersiliess" and password == "bog" else "user"

    user = User(username=username, password=password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    return db.query(User).filter_by(username=username, password=password).first()
