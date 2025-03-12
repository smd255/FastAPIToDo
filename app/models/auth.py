import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
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
    # アクセストークンとのリレーション
    access_tokens = relationship("UserAccessToken", back_populates="user")
    # リフレッシュトークンとのリレーション
    refresh_tokens = relationship("UserRefreshToken", back_populates="user")


# アクセストークン
class UserAccessToken(Base):
    __tablename__ = "user_access_tokens"

    # アクセストークンのID
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # ユーザーID
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    access_key: Mapped[str] = mapped_column(
        String(250), nullable=True, index=True, default=None
    )
    # 生成日
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    # トークン有効期限
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # トークンの有効/無効 ?
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # ユーザーテーブルとのrelation
    user = relationship("User", back_populates="access_tokens")


# リフレッシュトークン
class UserRefreshToken(Base):
    __tablename__ = "user_refresh_tokens"
    # リフレッシュトークンのID
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # ユーザーID
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # リフレッシュトークン
    refresh_key: Mapped[str] = mapped_column(
        String(250), nullable=True, index=True, default=None
    )
    # 生成日
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    # トークンの有効期限
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # トークンの有効/無効 ?
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # ユーザーテーブルとのrelation
    user = relationship("User", back_populates="refresh_tokens")
