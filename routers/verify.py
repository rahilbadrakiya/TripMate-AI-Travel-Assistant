from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
import crud, models, database

router = APIRouter()

@router.get("/verify-email/{token}", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    
    if not user:
        return """
        <html>
            <body style='font-family: Arial; text-align: center; padding-top: 50px;'>
                 <h1 style='color: red;'>Invalid Token</h1>
                 <p>The verification link is invalid or expired.</p>
            </body>
        </html>
        """

    if user.is_verified:
        return """
        <html>
            <body style='font-family: Arial; text-align: center; padding-top: 50px;'>
                 <h1 style='color: green;'>Already Verified</h1>
                 <p>Your account is already active. You can close this window and login.</p>
            </body>
        </html>
        """

    user.is_verified = True
    user.verification_token = None # Clear token after use (optional)
    db.commit()

    return """
    <html>
        <body style='font-family: Arial; text-align: center; padding-top: 50px;'>
             <h1 style='color: green;'>Email Verified!</h1>
             <p>Your account has been successfully activated.</p>
             <p>Return to the TripMate app to login.</p>
        </body>
    </html>
    """
