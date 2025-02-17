from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.util import ResponseSchema
from schemas.auth import InsertAndUpdateUserSchema
import cruds.auth as auth_crud
import db

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Auth"], prefix="/auth")


# 新規登録のエンドポイント
@router.post("/", response_model=ResponseSchema)
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
# どのURLから？ユーザー毎
