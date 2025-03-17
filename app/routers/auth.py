from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

import cruds.auth as auth_crud
from schemas.auth import UserResponseSchema, UserCreateSchema, TokenSchema
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
# TODO:有効時間が直値
@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def login(db: DbDependency, form_data: FormDependency):
    user = auth_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = auth_crud.create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
