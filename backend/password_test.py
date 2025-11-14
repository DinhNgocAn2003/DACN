from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def make_hash(password: str) -> str:
    pre = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(pre)


def verify(password: str, stored: str) -> bool:
    pre = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.verify(pre, stored)


if __name__ == "__main__":
    tests = [
        "a" * 10,
        "a" * 80,  # longer than bcrypt 72-byte limit
        "密码" * 40,  # multibyte characters
        "𠜎" * 40,  # supplementary Unicode (>1 codepoint bytes)
    ]

    for t in tests:
        h = make_hash(t)
        ok = verify(t, h)
        print(f"password(len={len(t)} chars, bytes={len(t.encode('utf-8'))}): verified={ok} stored_prefix={h[:6]}...")
