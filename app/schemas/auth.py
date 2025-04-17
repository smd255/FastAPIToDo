from pydantic import BaseModel, Field
from datetime import datetime


# ===========================================
# スキーマ定義
# ===========================================
# ユーザー登録時のスキーマ
class UserCreateSchema(BaseModel):
    username: str = Field(min_length=2, examples=["user1"])
    password: str = Field(min_length=8, examples=["test1234"])


# ユーザー登録結果のスキーマ
class UserResponseSchema(BaseModel):
    id: int = Field(gt=0, examples=[1])
    username: str = Field(min_length=2, examples=["user1"])
    created_at: datetime
    updated_at: datetime


# トークンのスキーマ
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


# デコードされたトークンのスキーマ
class DecodedTokenSchema(BaseModel):
    username: str
    user_id: int
