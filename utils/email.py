import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List

class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email@gmail.com"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your_app_password"),
    MAIL_FROM = os.getenv("MAIL_FROM", "your_email@gmail.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_verification_email(email: str, token: str):
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    verification_link = f"{base_url}/verify-email/{token}"
    
    html = f"""
    <h3>Verify your TripMate Account</h3>
    <p>Thanks for signing up! Click the link below to activate your account:</p>
    <a href="{verification_link}">Verify Email</a>
    <p>Or copy this link: {verification_link}</p>
    """

    message = MessageSchema(
        subject="TripMate - Verify your email",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"Email sent to {email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
