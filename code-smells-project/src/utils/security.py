import hashlib
import secrets


def hash_password(senha: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + senha).encode()).hexdigest()
    return f"{salt}:{digest}"


def verify_password(stored: str, provided: str) -> bool:
    if ':' not in stored:
        return stored == provided
    salt, digest = stored.split(':', 1)
    return hashlib.sha256((salt + provided).encode()).hexdigest() == digest
