"""Password hashing utilities (bcrypt)."""

import bcrypt

_BCRYPT_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    """Return bcrypt hash for storage in signon.password."""
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify plaintext against stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
