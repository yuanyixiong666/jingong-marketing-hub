"""
项目配置模块
AI生成：数据库连接配置、Redis配置、应用基础配置
人工修改：添加API认证密钥配置
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "金宫味业数字营销数据中台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "jingong_marketing"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # AI服务配置
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen3.7-max"

    @property
    def OPENAI_API_KEY(self) -> str:
        return self.DASHSCOPE_API_KEY

    @property
    def OPENAI_BASE_URL(self) -> str:
        return self.DASHSCOPE_BASE_URL

    # API服务地址（爬虫管道等模块统一使用此配置）
    API_BASE_URL: str = "http://localhost:8000"

    # API认证密钥（配置后所有接口需要携带 X-API-Key 请求头，留空则不认证）
    API_AUTH_KEY: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"


settings = Settings()
