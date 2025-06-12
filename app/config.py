from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ailist.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 存储配置
    UPLOAD_DIR: str = "uploads"
    
    # OpenAI配置
    OPENAI_API_KEY: str = "sk-4395efae45154eee884f0581b25b8a9b"
    
    # DeepSeek配置
    DEEPSEEK_API_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_CHAT_MODEL: str = "deepseek-chat"
    DEEPSEEK_EMBEDDING_MODEL: str = "deepseek-embed-2"
    
    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY
        
    @property
    def algorithm(self) -> str:
        return self.ALGORITHM
    
    class Config:
        env_file = ".env"

settings = Settings() 