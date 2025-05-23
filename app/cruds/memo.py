from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import schemas.memo as memo_schema
import models.memo as memo_model


# =============================================
# 非同期CRUD処理
# =============================================
# 新規登録
async def insert_memo(
    db_session: AsyncSession,
    memo_data: memo_schema.InsertAndUpdateMemoSchema,
    user_id: int,
) -> memo_model.Memo:
    print("=== 新規登録：開始 ===")
    # user_idを含む形でMemoモデルを作成
    memo_data_dict = memo_data.model_dump()
    memo_data_dict["user_id"] = user_id
    # new_memo = memo_model.Memo(**memo_data_dict.model_dump())
    new_memo = memo_model.Memo(**memo_data_dict)
    # DBに登録
    db_session.add(new_memo)
    await db_session.commit()
    await db_session.refresh(new_memo)  # DBの内容を変数に反映(DBの情報と同期)
    print(">>> データ追加完了")
    return new_memo


# ユーザー単位で全件取得
async def get_memos_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(memo_model.Memo).where(memo_model.Memo.user_id == user_id)
    )
    return result.scalars().all()


# 1件取得
async def get_memo_by_id(
    db_session: AsyncSession, memo_id: int
) -> memo_model.Memo | None:
    """
    データベースから特定のメモ１件取得する関数
    Args:
        db_session(AsyncSession): 非同期DBセッション
        memo_id(int): 取得するメモのID(プリマリーキー)
    Returns:
        Memo | None: 取得されたメモのモデル、メモが存在しない場合はNoneを返す
    """
    print("=== 1件取得：開始  ===")
    # 取得するメモをIDにより選択
    result = await db_session.execute(
        select(memo_model.Memo).where(memo_model.Memo.memo_id == memo_id)
    )
    memo = result.scalars().first()
    print(">>> データ取得完了")
    return memo


# 更新処理
async def update_memo(
    db_session: AsyncSession,
    memo_id: int,
    target_data: memo_schema.InsertAndUpdateMemoSchema,
) -> memo_model.Memo | None:
    """
    データベースのメモを更新する関数
    Args:
        db_session(AsyncSession): 非同期DBセッション
        memo_id(int): 更新するメモのID(プライマリーキー)
        target_date(InsertAndUpdateMemoSchema): 更新するデータ
    Returns:
        Memo | None: 更新されたメモのモデル、メモが存在しない場合はNoneを返す
    """
    print("=== データ更新：開始 ===")
    memo: memo_model.Memo = await get_memo_by_id(db_session, memo_id)  # 指定のメモ取得
    if memo:
        memo.title = target_data.title
        memo.description = target_data.description
        memo.is_check = target_data.is_check
        db_session.add(memo)
        await db_session.commit()
        await db_session.refresh(memo)
        print(">>> データ更新完了")

    return memo


# 削除処理
async def delete_memo(db_session: AsyncSession, memo_id: int) -> memo_model.Memo | None:
    """
    データベースのメモ削除する関数
    Args:
        db_session(AsyncSession): 非同期セッション
        memo_id(memo_id): 削除するメモのID(プライマリーキー)
    Returns:
        Memo | None: 削除されたメモのモデル、メモが存在しない場合はNoneを返す
    """
    print("=== データ削除：開始 ===")
    memo = await get_memo_by_id(db_session, memo_id)
    if memo:
        await db_session.delete(memo)
        await db_session.commit()
        print(">>> データ削除完了")

    return memo
