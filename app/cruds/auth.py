import base64
import hashlib
import os
from datetime import datetime, timedelta
import jwt

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.auth import UserCreateSchema, TokenSchema
from models.auth import User
from config import get_settings


ALGORITHM = "HS256"
SECRET_KEY = get_settings().secret_key

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ユーザー登録
async def create_user(
    db_session: AsyncSession, user_create: UserCreateSchema
) -> User | None:
    print("=== ユーザー新規登録：開始 ===")
    # ソルトの生成
    salt = base64.b64encode(os.urandom(32))
    # パスワードハッシュ化
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", user_create.password.encode(), salt, 1000
    ).hex()

    # TODO: 既存ユーザー名の重複チェック

    # ユーザ情報生成
    new_user = User(
        username=user_create.username, password=hashed_password, salt=salt.decode()
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)  # DBの内容を変数に反映(DBの情報と同期)
    print(">>> ユーザー追加完了")
    return new_user


# ユーザー認証
async def authenticate_user(
    db_session: AsyncSession, username: str, password: str
) -> User | None:
    # ユーザー名から選択
    user = await get_user_byname(db_session=db_session, username=username)
    if not user:
        return None

    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), user.salt.encode(), 1000
    ).hex()
    # パスワード失敗
    if user.password != hashed_password:
        return None

    return user


# ユーザー取得(ユーザー名)
async def get_user_byname(db_session: AsyncSession, username: str) -> User | None:
    result = await db_session.execute(select(User).where(User.username == username))
    print("=== ユーザー取得：開始  ===")
    user = result.scalars().first()
    if not user:
        return None
    print(">>> ユーザー取得完了")
    return user


# アクセストークン生成
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    expires = datetime.now() + expires_delta
    payload = {"sub": username, "id": user_id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# アクセストークン取得
def get_jwt_token(token: str = Depends(oauth2_schema)) -> TokenSchema:
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    return token


# Cookieから現在のユーザーを取得
# def get_current_user_from_cookie(request: Request) -> DecodedTokenSchema:
#     # Cookieからトークンを取得
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(
#             status_code=401, detail="Authentication credentials missing"
#         )

#     try:
#         # トークンをデコードしてペイロードを取得
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         exp = payload.get("exp")
#         if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(
#             timezone.utc
#         ):
#             raise HTTPException(status_code=401, detail="Token has expired")

#         # ユーザー情報を返す
#         return DecodedTokenSchema(
#             user_id=payload.get("id"), username=payload.get("sub")
#         )
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
