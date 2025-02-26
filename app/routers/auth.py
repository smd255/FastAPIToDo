from datetime import timedelta, datetime, timezone
import jwt
from typing import Union
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from schemas.util import ResponseSchema
from schemas.auth import InsertAndUpdateUserSchema, ResponseTokenSchema
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
    user: InsertAndUpdateUserSchema, db: AsyncSession = Depends(db.get_dbsession)
):
    try:
        # 新しいユーザー情報をDBに登録
        await auth_crud.insert_user(db, user)
        return ResponseSchema(message="ユーザーが正常に登録されました")
    except Exception:
        # 登録に失敗した場合、HTTP 400エラーを返す
        raise HTTPException(status_code=400, detail="ユーザーの登録に失敗しました。")


# ログインのエンドポイント
@router.post("/login", response_model=ResponseTokenSchema)
async def login(
    user: InsertAndUpdateUserSchema, db: AsyncSession = Depends(db.get_dbsession)
):
    try:
        # ユーザー, パスワード認証
        await auth_crud.verify_user(db, user)
        # トークンの発行
        # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # access_token = _create_access_token(
        #     data={"sub": user.user_id}, expires_delta=access_token_expires
        # )
        # JWTトークンの生成とクッキーへの設定
        # TODO: 関数コール
        return ResponseTokenSchema(access_token=access_token, token_type="bearer")
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
def _create_tokens()