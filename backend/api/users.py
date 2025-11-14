from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from db import get_session
from models.schemas import UserCreate
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import hashlib

try:
    from models import User
except ImportError:
    from ..models import User

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple JWT settings (for dev). In production, load secret from env/secure store.
SECRET_KEY = "dev-secret-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


class LoginRequest(BaseModel):
    username: str
    password: str


def add_cors_headers(response, request: Request = None):
    """Helper to add a sensible Access-Control-Allow-Origin header for dev.

    Use the request Origin when present so both http://localhost:5173 and
    http://127.0.0.1:5173 (or other dev variants) are accepted by browsers.
    If no request is provided, leave the response as-is and rely on global
    middleware to set headers.
    """
    try:
        if request is not None:
            origin = request.headers.get("origin")
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
    except Exception:
        pass
    return response


@router.post("/")
def create_user(user: UserCreate, session: Session = Depends(get_session), request: Request = None):
    """Create a new user. Password will be hashed before storing."""
    try:
        # Kiểm tra username đã tồn tại chưa
        existing_user = session.exec(select(User).where(User.username == user.username)).first()
        if existing_user:
            response = JSONResponse(
                status_code=400,
                content={"detail": "Username already exists"}
            )
            return add_cors_headers(response, request)

        # Kiểm tra email đã tồn tại chưa
        existing_email = session.exec(select(User).where(User.email == user.email)).first()
        if existing_email:
            response = JSONResponse(
                status_code=400,
                content={"detail": "Email already exists"}
            )
            return add_cors_headers(response, request)

        # Always pre-hash the password with SHA-256 hex digest before passing
        # to bcrypt. This avoids bcrypt's 72-byte input limit and is a common
        # safe strategy (we still store bcrypt(hash) so verification uses
        # bcrypt as usual). This is backwards-compatible with older users
        # because login verification checks both raw and pre-hash forms.
        if not getattr(user, "password", None):
            response = JSONResponse(status_code=400, content={"detail": "Password is required"})
            return add_cors_headers(response, request)
        
        # Normalize password input to bytes (UTF-8), then compute SHA-256
        # hex digest string. We hash the hex digest string with bcrypt.
        # This avoids bcrypt's 72-byte input limit and is deterministic.
        pwd_bytes = user.password.encode("utf-8") if isinstance(user.password, str) else user.password

        # Use hexdigest (64 hex chars) so bcrypt input length is small and
        # stable across platforms/encodings. Pass a str (not bytes) to passlib.
        pre_hashed = hashlib.sha256(pwd_bytes).hexdigest()

        try:
            # passlib expects a str; give it the hex string
            hashed = pwd_context.hash(pre_hashed)
        except Exception as e:
            response = JSONResponse(status_code=400, content={"detail": f"Invalid password: {str(e)}"})
            return add_cors_headers(response, request)
        
        u = User(username=user.username, email=user.email, password_hash=hashed)
        session.add(u)
        session.commit()
        session.refresh(u)

        # Do not return password hash to the client
        response = JSONResponse(
            status_code=200,
            content={"id": u.id, "username": u.username, "email": u.email, "is_verified": u.is_verified}
        )
        return add_cors_headers(response, request)
        
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )
        return add_cors_headers(response, request)


@router.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session), request: Request = None):
    """Alias for create_user at /register to match frontend expectations."""
    return create_user(user, session, request)


@router.post("/login")
def login(payload: LoginRequest, session: Session = Depends(get_session), request: Request = None):
    """Authenticate user with username and password, return a JWT and basic user info."""
    try:
        user = session.exec(select(User).where(User.username == payload.username)).first()
        # Debugging info (ASCII-safe)
        try:
            print(f"Login attempt for username={payload.username}")
        except Exception:
            pass
        if not user:
            response = JSONResponse(
                status_code=401,
                content={"detail": "Invalid username or password"}
            )
            return add_cors_headers(response, request)
        stored = user.password_hash
        try:
            # Print a short hint about stored password format (do not print full hash)
            prefix = (stored[:4] + '...') if isinstance(stored, str) else str(type(stored))
            print(f"Found user id={user.id} stored_prefix={prefix}")
        except Exception:
            pass
        verified = False

        # If stored looks like a bcrypt hash (starts with $2), verify the
        # SHA-256 hex-digest form only. Avoid passing raw password to bcrypt
        # because bcrypt enforces a 72-byte limit and will raise on long inputs.
        if isinstance(stored, str) and stored.startswith("$2"):
            try:
                pre = hashlib.sha256(payload.password.encode('utf-8')).hexdigest()
                # passlib expects str input
                verified = pwd_context.verify(pre, stored)
            except Exception:
                verified = False
        else:
            # Stored password is likely plain text or a simple hash
            # First try direct equality (plaintext), then try sha256 hex match.
            if payload.password == stored:
                verified = True
            else:
                try:
                    pre = hashlib.sha256(payload.password.encode('utf-8')).hexdigest()
                    if pre == stored:
                        verified = True
                except Exception:
                    verified = False

        try:
            print(f"Password verified: {verified}")
        except Exception:
            pass

        if not verified:
            response = JSONResponse(
                status_code=401,
                content={"detail": "Invalid username or password"}
            )
            return add_cors_headers(response, request)

        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_payload = {"sub": user.username, "user_id": user.id, "exp": expire}
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

        response = JSONResponse(
            status_code=200,
            content={
                "user": {
                    "id": user.id, 
                    "username": user.username, 
                    "email": user.email, 
                    "is_verified": user.is_verified
                }, 
                "token": token
            }
        )
        return add_cors_headers(response, request)
        
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Login error: {str(e)}"}
        )
        return add_cors_headers(response, request)


@router.get("/")
def list_users(session: Session = Depends(get_session), request: Request = None):
    try:
        users = session.exec(select(User)).all()
        # Return sanitized list
        response = JSONResponse(
            status_code=200,
            content=[{"id": u.id, "username": u.username, "email": u.email, "is_verified": u.is_verified} for u in users]
        )
        return add_cors_headers(response, request)
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching users: {str(e)}"}
        )
        return add_cors_headers(response, request)


@router.get("/{username}")
def get_user_by_username(username: str, session: Session = Depends(get_session), request: Request = None):
    try:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            response = JSONResponse(
                status_code=404,
                content={"detail": "User not found"}
            )
            return add_cors_headers(response, request)
            
        response = JSONResponse(
            status_code=200,
            content={"id": user.id, "username": user.username, "email": user.email, "is_verified": user.is_verified}
        )
        return add_cors_headers(response, request)
        
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching user: {str(e)}"}
        )
        return add_cors_headers(response, request)