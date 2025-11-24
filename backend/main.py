from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import users, events, nlp
from db import init_db
import uvicorn

# Scheduler reminders
from reminders import start_scheduler, stop_scheduler

app = FastAPI(title="Event Assistant API")

# Cấu hình CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo DB
init_db()

# Đăng ký routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(nlp.router, prefix="/nlp", tags=["nlp"])


@app.on_event("startup")
def _start_bg_tasks():
    # Bắt đầu scheduler background để kiểm tra và gửi email nhắc
    try:
        start_scheduler()
    except Exception as e:
        print(f"Failed to start reminder scheduler: {e}")


@app.on_event("shutdown")
def _stop_bg_tasks():
    try:
        stop_scheduler()
    except Exception:
        pass

# @app.get("/")
# async def root():
#     return {"status": "ok", "message": "Event Assistant API is running"}

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "Event Assistant API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)