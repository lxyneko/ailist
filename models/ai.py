from database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime

class FileAnalysis(Base):
    __tablename__ = 'file_analysis'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'))
    content_summary = Column(Text)
    suggested_tags = Column(Text)  # 存储为JSON字符串
    sentiment_score = Column(Integer)  # -100 到 100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 