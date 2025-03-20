from typing import Annotated
from datetime import timedelta

from starlette.status import HTTP_401_UNAUTHORIZED

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

import cruds.auth as auth_crud
from schemas.auth import (
    UserResponseSchema,
    UserCreateSchema,
    TokenSchema,
    DecodedTokenSchema,
)
import db

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Auth"], prefix="/auth")

# 依存性注入
DbDependency = Annotated[AsyncSession, Depends(db.get_dbsession)]
FormDependency = Annotated[OAuth2PasswordRequestForm, Depends()]


# =============================================
# ルート関数
# =============================================
# 新規登録のエンドポイント
@router.post(
    "/signup",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(db: DbDependency, user_create: UserCreateSchema):
    return auth_crud.create_user(db, user_create)


# ログインのエンドポイント
# TODO: 有効期間が直値
@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def login(db: DbDependency, form_data: FormDependency):
    user = auth_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # アクセストークンの生成
    token = auth_crud.create_access_token(user.username, user.id, timedelta(minutes=20))

    # Cookieを設定してレスポンスを作成
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # JavaScriptからアクセスできないようにする
        secure=True,  # HTTPSのみで送信する
        samesite="strict",  # CSRF攻撃を軽減するための設定
    )

    return response


# ログイン中のユーザーid取得
@router.get("/me", response_model=DecodedTokenSchema)
async def get_current_user_info(
    current_user: DecodedTokenSchema = Depends(auth_crud.get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )
    return current_user


# cokkieのjwtを認証チェック
