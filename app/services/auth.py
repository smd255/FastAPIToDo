from typing import Optional
from datetime import timedelta, datetime, timezone
import jwt

from fastapi import Cookie, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession


from config import settings, security
from util import unique_string

import schemas.auth as auth_schema
import cruds.auth as auth_crud


# =============================================
# 公開関数
# =============================================
# アクセストークン生成
async def create_tokens(user_id: int, db: AsyncSession, response: Response):
    # ユニークなキーを生成
    access_key = unique_string(50)
    refresh_key = unique_string(100)

    # トークンの有効期限を設定
    now = datetime.datetime.now(datetime.timezone.utc)  # 現在の時刻
    at_expires = _generate_expires(
        now=now, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    rt_expires = _generate_expires(
        now=now, minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    # アクセストークン保存
    at_token = await auth_crud.create_access_token(
        db_session=db,
        token=auth_schema.AccessTokenSchema(
            user_id=user_id, access_key=access_key, expires_at=at_expires
        ),
    )

    # リフレッシュトークン保存
    rt_token = await auth_crud.create_reflesh_token(
        db_session=db,
        token=auth_schema.RefleshTokenSchema(
            user_id=user_id, access_key=refresh_key, expires_at=rt_expires
        ),
    )

    # アクセストークンのペイロードを作成
    at_payload = {
        "sub": str(user_id),
        "jti": str(at_token.id),
        "type": "access",
        "exp": int((datetime.utcnow(timezone.utc) + at_expires).timestamp()),
        "iat": int(now.timestamp()),
    }

    # リフレッシュトークンのペイロードを作成
    rt_payload = {
        "sub": str(user_id),
        "jti": str(rt_token.id),
        "type": "refresh",
        "exp": int((now + rt_expires).timestamp()),
        "iat": int(now.timestamp()),
    }

    # JWTトークンを生成
    at_jwt = _generate_token(at_payload, settings.JWT_SECRET)
    rt_jwt = _generate_token(rt_payload, settings.JWT_REFRESH_SECRET)

    # クッキーにアクセストークンを設定
    response.set_cookie(
        key="access_token",
        value=f"Bearer {at_jwt}",
        httponly=True,
        secure=True,  # HTTPS環境では True に設定
        samesite="lax",  # 要件に応じて "strict" に変更可能
        max_age=int(at_expires.total_seconds()),
        expires=int((now + at_expires).timestamp()),
    )

    # クッキーにリフレッシュトークンを設定
    response.set_cookie(
        key="refresh_token",
        value=rt_jwt,
        httponly=True,
        secure=True,  # HTTPS環境では True に設定
        samesite="lax",  # 要件に応じて "strict" に変更可能
        max_age=int(rt_expires.total_seconds()),
        expires=int((now + rt_expires).timestamp()),
    )


# アクセストークンの取得
async def get_token_from_cookie(
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> str:
    """
    クッキーからアクセストークンを取得します。

    Args:
        access_token (Optional[str]): クッキーに格納されているアクセストークン。
            デフォルトは None。エイリアス "access_token" を使用してクッキーにアクセスします。

    Return:
        str: "Bearer " プレフィックスを削除したアクセストークン。

    Raises:
        HTTPException: アクセストークンが見つからない場合、または無効な場合に発生します。
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # トークンに "Bearer " プレフィックスがある場合は削除
    if access_token.startswith("Bearer "):
        access_token = access_token[7:]

    return access_token


# リフレッシュトークンの取得
async def get_refresh_token_from_cookie(
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token")
) -> str:
    """
    クッキーからリフレッシュトークンを取得します。

    Args:
        refresh_token (Optional[str]): クッキーに格納されているリフレッシュトークン。
            デフォルトは None。エイリアス "refresh_token" を使用してクッキーにアクセスします。

    Return:
        str: "Bearer " プレフィックスを削除したリフレッシュトークン。

    Raises:
        HTTPException: リフレッシュトークンが見つからない場合、または無効な場合に発生します。
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # トークンに "Bearer " プレフィックスがある場合は削除
    if refresh_token.startswith("Bearer "):
        refresh_token = refresh_token[7:]

    return refresh_token


# ペイロードの取得
async def get_token_payload(
    access_token: str = Depends(get_token_from_cookie),
    secret_key: str = security.SECRET_KEY,
):
    """
    アクセストークンからペイロードを取得します。

    Args:
        access_token (str): アクセストークン。
        secret_key (str): JWTのデコードに使用する秘密鍵。

    Return:
        dict: トークンのペイロード。

    Raises:
        HTTPException: トークンが無効な場合、またはデコードできない場合に発生します。
    """
    try:
        payload = jwt.decode(access_token, secret_key, security.ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# トークンの無効化(削除)
async def invalidate_token(db: AsyncSession, at_id: str, rt_id: str):
    # アクセストークンの無効化
    auth_crud.invalidate_actoken(db_session=db, at_id=at_id)
    # リフレッシュトークンの無効化
    auth_crud.invalidate_retoken(db_session=db, rt_id=rt_id)


# =============================================
# 内部関数
# =============================================


# トークン有効期日の生成
def _generate_expires(now: datetime.datetime, minutes: int):
    """
    現在時刻、有効時間を受け取り、計算した期日を返す
    """
    return now + timedelta(minutes=minutes)


# JWTトークンの生成
def _generate_token(payload: dict, secret: str) -> str:
    """
    指定されたペイロードとシークレットを使用してJWTトークンを生成します。

    :param payload: トークンのペイロード（データ）
    :param secret: トークンを署名するためのシークレットキー
    :return: 生成されたJWTトークン
    """
    return jwt.encode(payload, secret, algorithm=security.ALGORITHM)
