from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, plan, recommend

app = FastAPI(title="ORBIS Planner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(plan.router)
app.include_router(recommend.router)

@app.get("/")
def home():
    return {"message": "Backend is running successfully ??"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "orbis_planners_api"}
