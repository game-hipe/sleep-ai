import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Config(BaseModel):
    database_url: str = Field(
        default=os.getenv("DATABASE_URL"), json_schema_extra={"env": "DATABASE_URL"}
    )
    gemini_api_key: str = Field(
        default=os.getenv("GEMINI_API_KEY"), json_schema_extra={"env": "GEMINI_API_KEY"}
    )
    gemini_model: str = Field(
        default=os.getenv("GEMINI_MODEL"), json_schema_extra={"env": "GEMINI_MODEL"}
    )
    bot_token: str = Field(
        default=os.getenv("BOT_TOKEN"), json_schema_extra={"env": "BOT_TOKEN"}
    )
    proxy: str | None = Field(
        default=os.getenv("PROXY"), json_schema_extra={"env": "PROXY"}
    )
    access_token: str | None = Field(
        default=os.getenv("ACCESS_TOKEN"), json_schema_extra={"env": "ACCESS_TOKEN"}
    )
    bot_url: str | None = Field(
        default=os.getenv("BOT_URL"), json_schema_extra={"env": "BOT_URL"}
    )


config = Config()
