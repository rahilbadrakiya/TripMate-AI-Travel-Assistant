import models
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from routers import chat, plan, recommend, auth, trips, verify

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ORBIS Planner API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(verify.router)
app.include_router(trips.router)
app.include_router(chat.router)
app.include_router(plan.router)
app.include_router(recommend.router)

@app.get("/")
def home():
    return {"message": "Backend is running successfully ??"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "orbis_planners_api"}

if __name__ == "__main__":
    import uvicorn
    # Host on 0.0.0.0 to allow access from other devices (like your phone)
    uvicorn.run(app, host="0.0.0.0", port=8000)
