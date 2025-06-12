from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ailist.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    # 导入所有模型，确保它们被注册到 Base.metadata
    from app.models.storage import Storage
    from app.models.file import File
    
    # 创建所有表
    Base.metadata.create_all(bind=engine) 