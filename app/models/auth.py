from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db import Base


# ============================================
# モデル
# ============================================
# ユーザー情報
class User(Base):
    # テーブル名
    __tablename__ = "users"
    # ユーザーID：PK：自動インクリメント
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    # ユーザー名：未入力不可
    username = Column(String(50), nullable=False)
    # ハッシュ化パスワード：未入力不可
    hashed_password = Column(String(255), nullable=False)
    # ソルト
    salt = Column(String, nullable=False)
    # 生成日
    created_at = Column(DateTime, default=datetime.now())
    # 更新日
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # リレーション
    memos = relationship("Memo", back_populates="user")
