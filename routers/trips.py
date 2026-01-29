from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas, database
from routers import auth

router = APIRouter(
    prefix="/trips",
    tags=["trips"],
    dependencies=[Depends(auth.get_current_user)] # Protect all trip routes
)

@router.post("/", response_model=schemas.Trip)
def create_trip(
    trip: schemas.TripCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_trip(db=db, trip=trip, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Trip])
def read_trips(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_trips(db=db, user_id=current_user.id)

@router.delete("/{trip_id}")
def delete_trip(
    trip_id: str, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    success = crud.delete_trip(db=db, trip_id=trip_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"status": "success", "message": "Trip deleted"}
