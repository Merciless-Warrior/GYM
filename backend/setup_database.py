from backend.app_models import Base, engine

# Створює всі таблиці згідно з описом у models
Base.metadata.create_all(bind=engine)

print("✅ Базу даних створено успішно!")
