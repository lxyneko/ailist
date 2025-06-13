from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Storage(Base):
    __tablename__ = 'storages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # local, s3
    config = Column(Text, nullable=False)  # JSON配置
    is_active = Column(Boolean, default=False)  # 是否激活
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    files = relationship('File', back_populates='storage')
    
    def __repr__(self):
        return f'<Storage {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'config': self.config,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 