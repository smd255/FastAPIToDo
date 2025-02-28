from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response

from config import security
from schemas.util import ResponseSchema
from services import auth as auth_service
import cruds.auth as auth_crud
import models.auth as auth_model
import db

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Auth"], prefix="/auth")

# Bearerトークンの設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# =============================================
# ルート関数
# =============================================
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
        # JWTトークンの生成とクッキーへの設定
        await auth_service.create_tokens(user.id, db, response=response)
        return ResponseSchema(message="ログイン成功しました")
    except Exception:
        # 登録失敗時にHTTP400エラー(ユーザー名、パスワードミス以外の理由)
        raise HTTPException(status_code=400, detail="ログインに失敗しました。")


# トークンのリフレッシュ
@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
async def user_refresh_token(
    response: Response,
    db: AsyncSession = Depends(db.get_dbsession),
    access_token: str = Depends(auth_service.get_token_from_cookie),
    refresh_token: str = Depends(auth_service.get_refresh_token_from_cookie),
) -> bool:
    rt_token_payload = auth_service.get_token_payload(
        refresh_token, security.SECRET_KEY
    )

    if not rt_token_payload:
        return ResponseSchema(message="エラー。リフレッシュトークンがありません")

    at_token_payload = auth_service.get_token_payload(access_token, security.SECRET_KEY)
    if not at_token_payload:
        return ResponseSchema(message="エラー。アクセストークンがありません")
    rt_id = rt_token_payload.get("jti")
    at_id = at_token_payload.get("jti")
    if not rt_id or not at_id:
        return ResponseSchema(message="エラー。トークンがありません")

    # トークンの無効化
    # TODO:"POST"といっておきながらここの処理はPUT相当。要件等
    user_token = await auth_service.invalidate_token(db, at_id, rt_id)
    if not user_token:
        return False
    user: auth_model.User = user_token.user

    # トークンの生成
    # アクセストークン、リフレッシュトークン両方生成
    # リフレッシュトークンの有効期間もリセットされることになる。
    auth_service.create_tokens(user.id, db, response=response)
    return True
