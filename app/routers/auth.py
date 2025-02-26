from util import unique_string
from datetime import timedelta, datetime, timezone
import jwt
from typing import Union
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from config import settings
from schemas.util import ResponseSchema

import schemas.auth as auth_schema
import cruds.auth as auth_crud
import db

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Auth"], prefix="/auth")

# セキュリティ設定
# TODO:本番では別にする
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Bearerトークンの設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# 新規登録のエンドポイント
@router.post("/register", response_model=ResponseSchema)
async def create_user(
    data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(db.get_dbsession),
):
    try:
        # 新しいユーザー情報をDBに登録
        await auth_crud.insert_user(db, data)
        return ResponseSchema(message="ユーザーが正常に登録されました")
    except Exception:
        # 登録に失敗した場合、HTTP 400エラーを返す
        raise HTTPException(status_code=400, detail="ユーザーの登録に失敗しました。")


# ログインのエンドポイント
@router.post("/login", response_model=ResponseSchema)
async def login(
    response: Response,
    data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(db.get_dbsession),
):
    try:
        # ユーザー, パスワード認証
        user = await auth_crud.verify_user(db, data)
        # トークンの発行
        # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # access_token = _create_access_token(
        #     data={"sub": user.user_id}, expires_delta=access_token_expires
        # )
        # JWTトークンの生成とクッキーへの設定
        await _create_tokens(user.id, db, is_admin=False, response=response)
        return ResponseSchema(message="ログイン成功しました")
        # return {"access_token": access_token, "token_type": "bearer"}
        # return ResponseSchema(message="ログイン成功しました")
    except Exception:
        # 登録失敗時にHTTP400エラー(ユーザー名、パスワードミス以外の理由)
        raise HTTPException(status_code=400, detail="ログインに失敗しました。")


# =============================================
# 内部関数
# =============================================
# アクセストークン生成
# def _create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# アクセストークン生成
async def _create_tokens(user_id: int, db: AsyncSession, response: Response):
    # ユニークなキーを生成
    access_key = unique_string(50)
    refresh_key = unique_string(100)

    # トークンの有効期限を設定
    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    # アクセストークン保存
    # TODO: 時間はこれで良いか？
    await auth_crud.create_access_token(
        db_session=db,
        token=auth_schema.AccessTokenSchema(
            user_id=user_id, access_key=access_key, expires_at=at_expires
        ),
    )

    # リフレッシュトークン保存
    await auth_crud.create_reflesh_token(
        db_session=db,
        token=auth_schema.RefleshTokenSchema(
            user_id=user_id, access_key=refresh_key, expires_at=rt_expires
        ),
    )

    # アクセストークンのペイロードを作成
    ここから
