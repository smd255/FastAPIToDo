from fastapi import APIRouter

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Auth"], prefix="/auth")

# ログインのエンドポイント


# 新規登録のエンドポイント
