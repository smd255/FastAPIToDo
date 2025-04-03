from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

# from fastapi.responses import JSONResponse

import cruds.auth as auth_crud
from schemas.auth import (
    UserResponseSchema,
    UserCreateSchema,
    TokenSchema,
)
from models.auth import User
import db

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Auth"], prefix="/auth")

# 依存性注入
# DbDependency = Annotated[AsyncSession, Depends(db.get_dbsession)]
# FormDependency = Annotated[OAuth2PasswordRequestForm, Depends()]


# =============================================
# ルート関数
# =============================================
# 新規登録のエンドポイント
@router.post(
    "/signup",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreateSchema,
    db_session: AsyncSession = Depends(db.get_dbsession),
):
    new_user: User = await auth_crud.create_user(db_session, user_create)

    return UserResponseSchema(
        id=new_user.user_id,
        username=new_user.username,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
    )


# ログインのエンドポイント
# レスポンスでトークンを返し、Authorizationヘッダーへの格納を期待
# TODO:トークン保存期間が直値
@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def login(
    db_session: AsyncSession = Depends(db.get_dbsession),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    # デバッグ用
    print("ユーザー名" + form_data.username)
    print("パスワード" + form_data.password)
    user = await auth_crud.authenticate_user(
        db_session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = auth_crud.create_access_token(
        user.username, user.user_id, timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}
