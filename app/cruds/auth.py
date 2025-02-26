from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status

from passlib.context import CryptContext

import schemas.auth as auth_schema
import models.auth as auth_model

# パスワードハッシュ化,検証設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================
# 非同期CRUD処理
# =============================================
# 新規登録
# POST
async def insert_user(
    db_session: AsyncSession, data: OAuth2PasswordRequestForm
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
    hashed_password = _get_password_hash(data.password)  # パスワードハッシュ化
    new_user = auth_model.User(username=data.username, hashed_password=hashed_password)
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    print(">>> ユーザー情報追加完了")
    return new_user


# ログイン
# POST
async def verify_user(
    db_session: AsyncSession, data: OAuth2PasswordRequestForm
) -> auth_model.User:
    """
    ユーザーの検証
    Ards:
        db_session (AsyncSession): 非同期DBセッション
        user_data(InsertAndUpdateUserSchema): ログインするユーザーのデータ
    Return:
        認証できたユーザー
    """
    print("=== ユーザー照合開始 ===")
    result = await db_session.execute(
        select(auth_model.User).where(auth_model.User.username == data.username)
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名が間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not _verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="パスワードが間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# TODO：ユーザー情報の削除, 更新


# アクセストークン保存
async def create_access_token(
    db_session: AsyncSession, schema: auth_schema.AccessTokenSchema
):
    print("=== アクセストークン保存開始 ===")
    new_token = auth_model.UserAccessToken(
        user_id=schema.user_id,
        access_key=schema.access_key,
        expires_at=schema.expires_at,
    )
    db_session.add(new_token)
    await db_session.commit()
    await db_session.refresh(new_token)
    print(">>> アクセストークン保存完了")


# リフレッシュトークン保存
async def create_reflesh_token(
    db_session: AsyncSession, schema: auth_schema.RefleshTokenSchema
):
    print("=== リフレッシュトークン保存開始 ===")
    new_token = auth_model.UserRefreshToken(
        user_id=schema.user_id,
        access_key=schema.access_key,
        expires_at=schema.expires_at,
    )
    db_session.add(new_token)
    await db_session.commit()
    await db_session.refresh(new_token)
    print(">>> リフレッシュトークン保存完了")


# =============================================
# 内部関数
# =============================================
# パスワード検証
def _verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# パスワードハッシュ化
def _get_password_hash(password):
    return pwd_context.hash(password)
