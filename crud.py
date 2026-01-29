from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_trip(db: Session, trip: schemas.TripCreate, user_id: int):
    # Convert Pydantic models to JSON/Dict for storage if needed, 
    # but SQLAlchemy handles JSON fields pretty well if mapped correctly.
    # Pydantic .dict() or .model_dump() helps.
    
    trip_data = trip.dict(exclude={"flights"}) # Flights stored separately in JSON column
    flights_json = [f.dict() for f in (trip.flights or [])]
    
    db_trip = models.Trip(
        **trip_data,
        user_id=user_id,
        flights_data=flights_json # Store as JSON list
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def get_trips(db: Session, user_id: int):
    trips = db.query(models.Trip).filter(models.Trip.user_id == user_id).order_by(models.Trip.created_at.desc()).all()
    # Map back to Pydantic schema structure if needed, 
    # but strictly speaking FastAPI response_model handles it if attributes match.
    # We might need to map `flights_data` back to `flights` attribute manually if names differ,
    # but here I named the DB column `flights_data`. schema expects `flights`.
    
    result = []
    for t in trips:
        # Convert DB object to Schema compatible dict
        t_dict = t.__dict__.copy()
        t_dict["flights"] = t.flights_data
        result.append(t_dict)
    return result

def delete_trip(db: Session, trip_id: str, user_id: int):
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.user_id == user_id).first()
    if db_trip:
        db.delete(db_trip)
        db.commit()
        return True
    return False
