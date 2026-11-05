"""Password hashing tests (SEC-T-001)."""

from jpetstore.security.passwords import hash_password, verify_password


def test_bcrypt_hash_and_verify() -> None:
    hashed = hash_password("j2ee")
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password("j2ee", hashed)
    assert not verify_password("wrong", hashed)


def test_hash_is_not_plaintext() -> None:
    plain = "ACID"
    hashed = hash_password(plain)
    assert plain not in hashed
