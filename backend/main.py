import os
import traceback
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from .database import init_db, get_db
from .auth import hash_password, verify_password, create_access_token, get_current_user_from_token
from .interview import router as interview_router
from .dashboard import router as dashboard_router
from .history import router as history_router

app = FastAPI(
    title="AI Interview Coach Backend API",
    description="Full-stack AI Interview Preparation & Evaluation Platform API",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Unhandled Exception Handler (Guarantees JSON error responses)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"\n[Unhandled Backend Error] {request.method} {request.url.path}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Startup Database Initialization
@app.on_event("startup")
def startup_event():
    init_db()

# --- Auth Pydantic Schemas ---
class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

# --- Auth Routes ---
@app.post("/api/register")
def register(req: RegisterSchema):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (req.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email address is already registered.")
    
    pw_hash = hash_password(req.password)
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (req.name, req.email, pw_hash))
    user_id = cursor.lastrowid
    conn.close()

    token = create_access_token({"sub": str(user_id), "name": req.name, "email": req.email})
    return {"message": "Registration successful", "token": token, "user": {"id": user_id, "name": req.name, "email": req.email}}

@app.post("/api/login")
def login(req: LoginSchema):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users WHERE email = %s", (req.email,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email address or password.")

    token = create_access_token({"sub": str(user["id"]), "name": user["name"], "email": user["email"]})
    return {"message": "Login successful", "token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

@app.post("/api/logout")
def logout():
    return {"message": "Logout successful."}

@app.get("/api/user/profile")
def get_profile(current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user": user}

# Include Modular Routers
app.include_router(interview_router)
app.include_router(dashboard_router)
app.include_router(history_router)

# Mount Frontend Static Files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend_static")

@app.get("/{full_path:path}")
def serve_frontend_pages(full_path: str):
    file_path = os.path.join(frontend_dir, full_path)
    if full_path and os.path.isfile(file_path):
        res = FileResponse(file_path)
        res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        res.headers["Pragma"] = "no-cache"
        res.headers["Expires"] = "0"
        return res
    
    # Map root or html requests
    if not full_path or full_path == "/" or full_path == "index":
        target = os.path.join(frontend_dir, "index.html")
    else:
        target = os.path.join(frontend_dir, f"{full_path}.html")
        if not os.path.exists(target):
            target = os.path.join(frontend_dir, "index.html")

    if os.path.exists(target):
        res = FileResponse(target)
        res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        res.headers["Pragma"] = "no-cache"
        res.headers["Expires"] = "0"
        return res
    return JSONResponse(status_code=404, content={"detail": "Page not found."})
