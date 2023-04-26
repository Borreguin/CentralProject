import bcrypt


def get_hashed_text(plain_text: str) -> bytes:
    return bcrypt.hashpw(plain_text.encode('utf8'), bcrypt.gensalt())


def verify_hashed_text(plain_text: str, hashed_text: bytes) -> bool:
    return bcrypt.checkpw(plain_text.encode('utf8'), hashed_text)
