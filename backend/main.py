from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import users, events, nlp
from db import init_db

app = FastAPI(title="Event Assistant API")

# CORS configuration
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

@app.get("/")
async def root():
    return {"status": "ok", "message": "Event Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Event Assistant API"}

# Debug endpoint để kiểm tra tất cả routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        route_info = {
            "path": getattr(route, "path", None),
            "name": getattr(route, "name", None),
            "methods": list(getattr(route, "methods", [])) if hasattr(route, "methods") else None
        }
        routes.append(route_info)
    return {"routes": routes}

# Xử lý preflight OPTIONS requests
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    # print("🚀 Starting Event Assistant API on http://0.0.0.0:8000")
    # print("🔧 CORS enabled for:")
    # for origin in ALLOWED_ORIGINS:
        # print(f"   - {origin}")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)