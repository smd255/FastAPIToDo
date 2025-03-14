from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import services.auth as auth_service


class JWTAuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
        auth_service: auth_service.AuthService = Depends(auth_service.get_auth_service),
    ) -> Optional[HTTPAuthorizationCredentials]:
        try:
            # Cookieからトークンを取得
            access_token = auth_service.get_token_from_cookie()
            # アクセスト－クンがあるとき
            if access_token is not None:
                # まずアクセストークンの検証を試みる
                if access_token:
                    is_valid = await auth_service.validate_token(access_token)
                    if is_valid:
                        return HTTPAuthorizationCredentials(
                            scheme="Bearer", credentials=access_token
                        )
            else:
                # アクセストークンが無い場合
                if リフレッシュトークンが有効か？ :
                    アクセストークンの再発行
                    該当ページに再アクセス(どうやって?)
                else
                    ログインページに移行(URL送る？)
        except Exception:
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="認証失敗",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None