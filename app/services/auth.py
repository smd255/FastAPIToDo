from typing import Optional
from datetime import timedelta, datetime, timezone
import jwt

from fastapi import ExpiredSignatureError, InvalidTokenError
from fastapi import Cookie, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession


from config import settings, security
from util import unique_string
import schemas.auth as auth_schema
import cruds.auth as auth_crud


# トークンの管理(ビジネスロジック部分)


# =============================================
# クラス定義
# =============================================
class AuthService:
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

    # ================================
    # 公開メソッド
    # ================================
    # トークンの検証
    async def validate_token(self, token: str) -> bool:
        try:
            # トークンをデコードし、署名とペイロードを検証
            # セキュリティはリストとして渡すことを推奨
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=self.algorithm
            )
            if decoded_token is not None:
                # トークンが有効な場合はTrueを返す
                # 例外発生により無効判定
                return True
            print("トークンの取得失敗")
            return False
        except ExpiredSignatureError:
            # トークンが期限切れの場合の処理
            print("トークンの期限切れ")
            return False
        except InvalidTokenError:
            # トークンが無効な場合の処理
            print("トークンが無効")
            return False
        except Exception as e:
            # その他のエラーが発生した場合は外部へスローする。
            print(f"その他エラー発生: {str(e)}")
            raise e

    async def refresh_token(self, response: Response, token: str) -> bool:
        作成中
        # リフレッシュトークンのロジック
        # 新しいアクセストークンを発行して、レスポンスに設定
        if token == "refresh":
            create_tokens()  # アクセストークン再発行, リフレッシュトークン再生成
            return True
        return False

    async def get_user_id_from_token(self, token: str) -> Optional[str]:
        作成中
        # トークンからユーザーIDを取得するロジック
        # ここでは簡単にトークンが"valid"ならユーザーIDを返す
        if token == "valid":
            return "user_id"
        return None


# =============================================
# 公開関数
# =============================================
# AuthServiceインスタンスを返す
auth_service_instance = AuthService(
    secret_key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
)


def get_auth_service() -> AuthService:
    return auth_service_instance


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


# JWTの生成
def _generate_token(payload: dict, secret: str) -> str:
    """
    指定されたペイロードとシークレットを使用してJWTを生成します。

    :param payload: トークンのペイロード（データ）
    :param secret: トークンを署名するためのシークレットキー
    :return: 生成されたJWT
    """
    return jwt.encode(payload, secret, algorithm=security.ALGORITHM)
