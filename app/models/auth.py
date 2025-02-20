from sqlalchemy import Column, Integer, String
from db import Base


# ============================================
# モデル
# ============================================
# memosテーブル用：モデル
class User(Base):
    # テーブル名
    __tablename__ = "users"
    # ユーザーID：PK：自動インクリメント
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    # ユーザー名：未入力不可
    username = Column(String(50), nullable=False)
    # ハッシュ化パスワード：未入力不可
    hashed_password = Column(String(255), nullable=False)
