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
    user = auth_crud.authenticate_user(
        db_session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = auth_crud.create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}


# ログイン中のユーザーid取得
# コールされていない、不要?
# @router.get("/me", response_model=DecodedTokenSchema)
# async def get_current_user_info(
#     current_user: DecodedTokenSchema = Depends(auth_crud.get_jwt_token),
# ):
#     if not current_user:
#         raise HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
#         )
#     デコード後のschemaで良いのか？
#     return current_user


# ログインのエンドポイント
# OLD:Cookieに保存している。
# @router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenSchema)
# async def login(
#     db: AsyncSession = Depends(db.get_dbsession),
#     form_data: OAuth2PasswordRequestForm = Depends,
# ):
#     user = auth_crud.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")

#     # アクセストークンの生成
#     token = auth_crud.create_access_token(user.username, user.id, timedelta(minutes=20))

#     # Cookieを設定してレスポンスを作成
#     response = JSONResponse(content={"message": "Login successful"})
#     response.set_cookie(
#         key="access_token",
#         value=token,
#         httponly=True,  # JavaScriptからアクセスできないようにする
#         secure=True,  # HTTPSのみで送信する
#         samesite="strict",  # CSRF攻撃を軽減するための設定
#     )

#     return response
