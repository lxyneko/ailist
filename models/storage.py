from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Storage(Base):
    __tablename__ = 'storages'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # 'local' 或 's3'
    config = Column(Text, nullable=False)  # JSON 格式的配置信息
    is_active = Column(Integer, default=0)  # 0: 非活动, 1: 活动
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'config': self.config,
            'is_active': self.is_active,
            'created_at': str(self.created_at) # Convert datetime to string for JSON serialization
        } 