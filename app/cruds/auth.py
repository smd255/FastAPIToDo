from sqlalchemy.ext.asyncio import AsyncSession
import schemas.auth as auth_schema
import models.auth as auth_model
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================
# 非同期CRUD処理
# =============================================
# 新規登録
# POST
async def insert_user(
    db_session: AsyncSession, user_data: auth_schema.InsertAndUpdateUserSchema
) -> auth_model.User:
    """
    ユーザー情報をデータベースに新規登録する関数
    Ards:
        db_session (AsyncSession): 非同期DBセッション
        user_data(InsertAndUpdateUserSchema): 登録するユーザーのデータ
    Return:
        User: 登録されたユーザーのモデル
    """
    print("=== ユーザー登録：開始 ===")
    hasshed_password = pwd_context.hash(user_data.password)  # パスワードハッシュ化
    new_user = auth_model.User(
        username=user_data.username, hasshed_password=hasshed_password
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    print(">>> ユーザー情報追加完了")
    return new_user


# ログイン
# GET
# GETして照合する


# TODO：ユーザー情報の削除, 更新
