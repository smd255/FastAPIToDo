from datetime import timedelta, datetime, timezone
import jwt
from typing import Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import schemas.auth as auth_schema
import models.auth as auth_model

# セキュリティ設定
# TODO:本番では別にする
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Bearerトークンの設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# パスワードハッシュ化,検証設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================
# 非同期CRUD処理
# =============================================
# 新規登録
# POST
async def insert_user(
    db_session: AsyncSession, user_data: auth_schema.InsertAndUpdateUserSchema
) -> auth_model.User:
    """
    ユーザー情報をデータベースに新規登録する関数
    Ards:
        db_session (AsyncSession): 非同期DBセッション
        user_data(InsertAndUpdateUserSchema): 登録するユーザーのデータ
    Return:
        User: 登録されたユーザーのモデル
    """
    print("=== ユーザー登録：開始 ===")
    hashed_password = _get_password_hash(user_data.password)  # パスワードハッシュ化
    new_user = auth_model.User(
        username=user_data.username, hashed_password=hashed_password
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    print(">>> ユーザー情報追加完了")
    return new_user


# ログイン
# POST
async def login(
    db_session: AsyncSession, user_data: auth_schema.InsertAndUpdateUserSchema
) -> dict | None:
    """
    ユーザーの検証
    Ards:
        db_session (AsyncSession): 非同期DBセッション
        user_data(InsertAndUpdateUserSchema): ログインするユーザーのデータ
    Return:
        dict: アクセストークン, トークンタイプ
    """
    print("=== ユーザー照合開始 ===")
    result = await db_session.execute(
        select(auth_model.User).where(auth_model.User.username == user_data.username)
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名が間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not _verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="パスワードが間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = _create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# TODO：ユーザー情報の削除, 更新


# =============================================
# 内部関数
# =============================================
# パスワード検証
def _verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# パスワードハッシュ化
def _get_password_hash(password):
    return pwd_context.hash(password)


# アクセストークン生成
def _create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
