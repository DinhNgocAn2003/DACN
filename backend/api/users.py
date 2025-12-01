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

# Endpoints quản lý người dùng: tạo, đăng ký, đăng nhập, liệt kê, lấy theo username

# Băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cấu hình JWT (dev). Trong production, lấy secret từ biến môi trường
SECRET_KEY = "dev-secret-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 ngày


class LoginRequest(BaseModel):
    username: str
    password: str


def add_cors_headers(response, request: Request = None):
    """Thêm header CORS phù hợp cho môi trường dev (ngắn gọn)."""
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
# Tạo user mới
def create_user(user: UserCreate, session: Session = Depends(get_session), request: Request = None):
    """Tạo user mới. Mật khẩu được băm trước khi lưu."""
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

        # Luôn pre-hash bằng SHA-256 trước khi đưa cho bcrypt để tránh giới hạn 72 bytes
        # Lưu bcrypt(pre_hashed) và so sánh khi đăng nhập.
        if not getattr(user, "password", None):
            response = JSONResponse(status_code=400, content={"detail": "Password is required"})
            return add_cors_headers(response, request)
        
        # Chuyển password sang bytes (UTF-8) rồi lấy SHA-256 hexdigest
        # Sau đó băm hexdigest bằng bcrypt.
        pwd_bytes = user.password.encode("utf-8") if isinstance(user.password, str) else user.password

        # Dùng hexdigest (64 ký tự) để đảm bảo độ dài nhỏ và ổn định.
        pre_hashed = hashlib.sha256(pwd_bytes).hexdigest()

        try:
            # passlib nhận str; truyền hex string
            hashed = pwd_context.hash(pre_hashed)
        except Exception as e:
            response = JSONResponse(status_code=400, content={"detail": f"Invalid password: {str(e)}"})
            return add_cors_headers(response, request)
        
        u = User(username=user.username, email=user.email, password_hash=hashed)
        session.add(u)
        session.commit()
        session.refresh(u)

        # Không trả password hash cho client
        response = JSONResponse(
            status_code=200,
            content={"id": u.id, "username": u.username, "email": u.email}
        )
        return add_cors_headers(response, request)
        
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )
        return add_cors_headers(response, request)


@router.post("/register")
# Đăng ký (alias)
def register(user: UserCreate, session: Session = Depends(get_session), request: Request = None):
    """Alias cho /register (để frontend tương thích)."""
    return create_user(user, session, request)


@router.post("/login")
# Đăng nhập và trả JWT
def login(payload: LoginRequest, session: Session = Depends(get_session), request: Request = None):
    """Xác thực user, trả JWT và thông tin cơ bản."""
    try:
        user = session.exec(select(User).where(User.username == payload.username)).first()
        # Thông tin debug (ASCII-safe)
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
            # In ra gợi ý ngắn về định dạng hash (không in toàn bộ hash)
            prefix = (stored[:4] + '...') if isinstance(stored, str) else str(type(stored))
            print(f"Found user id={user.id} stored_prefix={prefix}")
        except Exception:
            pass
        verified = False

        # Nếu stored là bcrypt (bắt đầu bằng $2), so sánh với SHA-256 hexdigest
        # Tránh truyền raw password vào bcrypt vì giới hạn 72 bytes.
        if isinstance(stored, str) and stored.startswith("$2"):
            try:
                pre = hashlib.sha256(payload.password.encode('utf-8')).hexdigest()
                # passlib expects str input
                verified = pwd_context.verify(pre, stored)
            except Exception:
                verified = False
        else:
            # Nếu không phải bcrypt, thử so sánh trực tiếp rồi thử sha256 hexdigest
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
                    "email": user.email
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
# Liệt kê người dùng (đã lọc dữ liệu nhạy cảm)
def list_users(session: Session = Depends(get_session), request: Request = None):
    try:
        users = session.exec(select(User)).all()
        # Trả về danh sách user đã loại bỏ thông tin nhạy cảm
        response = JSONResponse(
            status_code=200,
            content=[{"id": u.id, "username": u.username, "email": u.email} for u in users]
        )
        return add_cors_headers(response, request)
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching users: {str(e)}"}
        )
        return add_cors_headers(response, request)


@router.get("/{username}")
# Lấy thông tin user theo username
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
            content={"id": user.id, "username": user.username, "email": user.email}
        )
        return add_cors_headers(response, request)
        
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching user: {str(e)}"}
        )
        return add_cors_headers(response, request)