from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import crud

def check_user(email):
    db = SessionLocal()
    try:
        user = crud.get_user_by_email(db, email=email)
        if user:
            print(f"User found: ID={user.id}, Email={user.email}, Name={user.name}, Verified={user.is_verified}")
            print(f"Hashed Password: {user.hashed_password}")
        else:
            print("User NOT found in database.")
            
        # List all users just in case
        print("\n--- All Users ---")
        users = db.query(models.User).all()
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_user("") # Just to trigger imports if needed, but we'll focus on the listing part
    
    print("\n--- DUMPING ALL USERS ---")
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        if not users:
            print("No users found in database.")
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}, Name: {u.name}, Verified: {u.is_verified}")
    finally:
        db.close()
