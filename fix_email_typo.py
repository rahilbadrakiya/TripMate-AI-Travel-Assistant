from database import SessionLocal
import models

def fix_email():
    db = SessionLocal()
    try:
        # specific fix for the user found
        user = db.query(models.User).filter(models.User.email == "rahilbadrakiya3131@gmail.co").first()
        if user:
            print(f"Found user with typo: {user.email}")
            user.email = "rahilbadrakiya3131@gmail.com"
            db.commit()
            print(f"Updated email to: {user.email}")
        else:
            print("User with typo not found.")
            
        # Verify
        user_fixed = db.query(models.User).filter(models.User.email == "rahilbadrakiya3131@gmail.com").first()
        if user_fixed:
            print(f"Verification: User exists now as {user_fixed.email}")
            
    finally:
        db.close()

if __name__ == "__main__":
    fix_email()
