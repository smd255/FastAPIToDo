from pydantic import BaseModel, Field


# ===========================================
# スキーマ定義
# ===========================================
# レスポンスで使用する結果用スキーマ
class ResponseSchema(BaseModel):
    # 処理結果のメッセージ。このフィールドは必須。
    message: str = Field(
        ...,
        description="API操作の結果を説明するメッセージ",
        example="メモの更新に成功しました。",
    )
