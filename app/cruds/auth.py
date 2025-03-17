import base64
import hashlib
import os
from datetime import datetime, timedelta
import jwt
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.auth import UserCreateSchema, DecodedTokenSchema
from models.auth import User
from config import get_settings


ALGORITHM = "HS256"
SECRET_KEY = get_settings().secret_key

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ユーザー登録
def create_user(db: AsyncSession, user_create: UserCreateSchema) -> User | None:
    # ソルトの生成
    salt = base64.b64encode(os.urandom(32))
    # パスワードハッシュ化
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", user_create.password.encode(), salt, 1000
    ).hex()

    # ユーザ情報生成
    new_user = User(
        username=user_create.username, password=hashed_password, salt=salt.decode()
    )
    db.add(new_user)
    db.commit()

    return new_user


# ユーザー認証
def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    # ユーザー名から選択
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), user.salt.encode(), 1000
    ).hex()
    # パスワード失敗
    if user.password != hashed_password:
        return None

    return user


# アクセストークン生成
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    expires = datetime.now() + expires_delta
    payload = {"sub": username, "id": user_id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 現在のユーザー取得
def get_current_user(token: Annotated[str, Depends(oauth2_schema)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            return None
        return DecodedTokenSchema(username=username, user_id=user_id)
    except jwt.JWTError:
        raise jwt.JWTError
