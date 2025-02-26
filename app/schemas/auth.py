from pydantic import BaseModel, Field
from datetime import datetime

# TODO: 不要になる? OAuth2PasswordRequestForm を使えばいいから？

# ===========================================
# スキーマ定義
# ===========================================
# 登録・更新で使用するスキーマ
# class InsertAndUpdateUserSchema(BaseModel):
#     # メモのタイトル。このフィールドは必須。
#     # Field: SWaggerUIに表示する凡例
#     username: str = Field(
#         ...,
#         description="ユーザー名を入力してください。最低一文字以上は必要です。",
#         example="hoge",
#         min_length=1,
#     )
#     # メモの詳細説明。このフィールドは任意で入力可能。
#     password: str = Field(
#         description="パスワードを入力してください。",
#         example="1111",
#         # min_length=8,
#     )


# # ユーザー情報を表すスキーマ
# class UserSchema(InsertAndUpdateUserSchema):
#     # ユーザー一意識別子。データベースでユニークな主キーとして使用されます。
#     user_id: int = Field(
#         ...,
#         description="ユーザーを一意に識別するID番号。データベースで自動的に割り当てられます。",
#         example=123,
#     )

#     # ハッシュ化されたパスワード
#     # TODO:このくらす軽油の受け渡しは妥当か？
#     hashed_password: str = Field(
#         description="ハッシュ化されたパスワード",
#         example="????",
#         # min_length=8,
#     )


# # ログイン時のトークン生成結果のスキーマ
# class ResponseTokenSchema(BaseModel):
#     # 処理結果のメッセージ。このフィールドは必須。
#     access_token: str = Field(
#         description="生成したトークン",
#     )
#     token_type: str = Field(
#         description="トークンタイプ",
#         example="bearer",
#     )


# アクセストークンのスキーマ
class AccessTokenSchema(BaseModel):
    # ユーザーID
    user_id: int = Field(
        ...,
        description="ユーザーを一意に識別するID番号。ログインユーザーのIDを割り当てる",
        example=123,
    )
    access_key: str = Field(
        description="ユニークな文字列",
    )
    # トークン有効期限
    # TODO: 有効期限なら有効な時刻になる？？
    expires_at: datetime = Field(description="トークン有効期限")


# リフレッシュトークンのスキーマ
class RefleshTokenSchema(BaseModel):
    # ユーザーID
    user_id: int = Field(
        ...,
        description="ユーザーを一意に識別するID番号。ログインユーザーのIDを割り当てる",
        example=123,
    )
    access_key: str = Field(
        description="ユニークな文字列",
    )
    # トークン有効期限
    # TODO: 有効期限なら有効な時刻になる？？
    expires_at: datetime = Field(description="トークン有効期限")
