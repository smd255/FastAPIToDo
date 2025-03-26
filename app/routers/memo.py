from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.memo import InsertAndUpdateMemoSchema, MemoSchema, ResponseSchema
from schemas.auth import DecodedTokenSchema
import cruds.memo as memo_crud
import cruds.auth as auth_crud
import db

# ルーターを作成し、タグとURLパスのプレフィックスを認定
router = APIRouter(tags=["Memos"], prefix="/memos")


# ============================================
# メモ用のエンドポイント
# ============================================
# メモ新規登録のエンドポイント
@router.post("/{user_id}", response_model=ResponseSchema)
async def create_memo(
    memo: InsertAndUpdateMemoSchema,
    db: AsyncSession = Depends(db.get_dbsession),
    user: DecodedTokenSchema = Depends(auth_crud.get_jwt_token),
):
    try:
        # 現在のユーザーIDを取得
        user_id = user.user_id
        # 新しいメモをデータベースに登録
        await memo_crud.insert_memo(db, memo, user_id)
        return ResponseSchema(message="メモが正常に登録されました")
    except Exception:
        # 登録に失敗した場合、HTTP 400エラーを返す
        raise HTTPException(status_code=400, detail="メモの登録に失敗しました。")


# ユーザー単位でメモ情報全件取得のエンドポイント
@router.get("/{user_id}", response_model=list[MemoSchema])
async def get_memos_list(
    db: AsyncSession = Depends(db.get_dbsession),
    user: DecodedTokenSchema = Depends(auth_crud.get_jwt_token),
):
    # Cookieのuser_id(ログイン中のuser_id)のmemo取得
    memos = await memo_crud.get_memos_by_user_id(db, user.user_id)
    return memos


# 特定のメモ情報取得のエンドポイント
@router.get("/{user_id}/{memo_id}", response_model=MemoSchema)
async def get_memo_detail(
    memo_id: int,
    db: AsyncSession = Depends(db.get_dbsession),
    user=Depends(auth_crud.get_jwt_token),
):
    # 指定されたIDのメモをデータベースから取得
    memo = await memo_crud.get_memo_by_id(db, memo_id)

    if not memo:
        # メモが見つからない場合、HTTP 404エラーを返す
        raise HTTPException(status_code=404, detail="メモが見つかりません")

    if memo.user_id != user.user_id:
        # ログイン中のユーザーidと取得したメモのユーザーidが異なる場合、HTTP 404エラーを返す
        raise HTTPException(
            status_code=404, detail="該当ユーザーのメモが見つかりません"
        )
    return memo


# ユーザー単位で設定
# 特定のメモを更新するエンドポイント
@router.put("/{user_id}/{memo_id}", response_model=ResponseSchema)
async def modify_memo(
    memo_id: int,
    memo: InsertAndUpdateMemoSchema,
    db: AsyncSession = Depends(db.get_dbsession),
    user=Depends(auth_crud.get_jwt_token),
):
    # ユーザーIDチェック
    memo = await memo_crud.get_memo_by_id(db, memo_id)
    if memo.user_id != user.user_id:
        # ログイン中のユーザーidと取得したメモのユーザーidが異なる場合、HTTP 404エラーを返す
        raise HTTPException(
            status_code=404, detail="該当ユーザーのメモが見つかりません"
        )

    # 指定されたIDのメモを新しいデータで更新
    update_memo = await memo_crud.update_memo(db, memo_id, memo)
    if not update_memo:
        # 更新対象が見つからない場合、HTTP 404エラーを返す
        raise HTTPException(status_code=404, detail="更新対象が見つかりません")
    return ResponseSchema(message="メモが正常に更新されました")


# 特定のメモを削除するエンドポイント
@router.delete("/{user_id}/{memo_id}", response_model=ResponseSchema)
async def remove_memo(
    memo_id: int,
    db: AsyncSession = Depends(db.get_dbsession),
    user=Depends(auth_crud.get_jwt_token),
):
    # ユーザーIDチェック
    memo = await memo_crud.get_memo_by_id(db, memo_id)
    if memo.user_id != user.user_id:
        # ログイン中のユーザーidと取得したメモのユーザーidが異なる場合、HTTP 404エラーを返す
        raise HTTPException(
            status_code=404, detail="該当ユーザーのメモが見つかりません"
        )

    # 指定されたIDのメモをデータベースから削除
    result = await memo_crud.delete_memo(db, memo_id)
    if not result:
        # 削除対象が見つからない場合、HTTP 404エラーを返す
        raise HTTPException(status_code=404, detail="削除対象が見つかりません")

    return ResponseSchema(message="メモが正常に削除されました")
