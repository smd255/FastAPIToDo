from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

from db import Base


# ============================================
# モデル
# ============================================
# memosテーブル用：モデル
class Memo(Base):
    # テーブル名
    __tablename__ = "memos"
    # メモID：PK：自動インクリメント
    memo_id = Column(Integer, primary_key=True, autoincrement=True)
    # タイトル：未入力不可
    title = Column(String(50), nullable=False)
    # 詳細：未入力可
    description = Column(String(255), nullable=True)
    # チェック状況：True:チェック有り, False：チェック無し
    is_check = Column(Boolean, default=False)
    # ユーザーID：未入力不可
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    # 作成日時
    created_at = Column(DateTime, default=datetime.now())
    # 更新日時
    updated_at = Column(DateTime)

    # リレーション
    user = relationship("User", back_populates="memos")
