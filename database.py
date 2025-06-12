from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# 创建数据库引擎
engine = create_engine('sqlite:///ailist.db', convert_unicode=True)

# 创建会话工厂
db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

# 创建基类
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """初始化数据库"""
    # 导入所有模型，确保它们被注册到 Base.metadata
    import models.storage
    import models.file
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def shutdown_session(exception=None):
    """关闭数据库会话"""
    db_session.remove() 