from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth import AuthService, get_auth_service


class JWTAuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> Optional[HTTPAuthorizationCredentials]:
        try:
            # Cookieからトークンを取得
            access_token = request.cookies.get("access_token")
            # refresh_token = request.cookies.get("refresh_token")

            # if not access_token and not refresh_token:
            #     if self.auto_error:
            #         raise HTTPException(
            #             status_code=401,
            #             detail="No authentication token provided",
            #             headers={"WWW-Authenticate": "Bearer"},
            #         )
            #     return None

            # アクセスト－クンがあるとき
            if access_token is not None:
                # まずアクセストークンの検証を試みる
                if access_token:
                    is_valid = await auth_service.validate_token(access_token)
                    if is_valid:
                        return HTTPAuthorizationCredentials(
                            scheme="Bearer", credentials=access_token
                        )

                #
                # # アクセストークンが無効な場合、リフレッシュトークンを試す
                # if refresh_token:
                #     is_refreshed = await auth_service.refresh_token(
                #         response=request.state.response, token=refresh_token
                #     )
                #     if is_refreshed:
                #         # 新しいアクセストークンが発行されたので、次のリクエストで使用される
                #         return HTTPAuthorizationCredentials(
                #             scheme="Bearer", credentials=access_token
                #         )
            else:
                # アクセストークンが無い場合
                if リフレッシュトークンが有効か？ :
                    アクセストークンの再発行
                    該当ページに再アクセス(どうやって?)
                else
                    ログインページに移行(URL送る？)
                
            # どちらのトークンも無効な場合
            # if self.auto_error:
            #     raise HTTPException(
            #         status_code=401,
            #         detail="Invalid or expired token",
            #         headers={"WWW-Authenticate": "Bearer"},
            #     )
            # return None
        except Exception:
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="認証失敗",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None


# ミドルウェアを使用するためのDependency
async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(JWTAuthMiddleware()),
    auth_service: AuthService = Depends(get_auth_service),
) -> str:
    try:
        # トークンからユーザーIDを取得
        user_id = await auth_service.get_user_id_from_token(auth.credentials)
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )