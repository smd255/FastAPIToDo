import secrets
import string


# ユニークな文字列を生成
def unique_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))
