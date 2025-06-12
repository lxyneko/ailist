from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    path = Column(String(1000), nullable=False)
    size = Column(Integer, nullable=False)  # 文件大小（字节）
    type = Column(String(50), nullable=False)  # 文件类型
    storage_id = Column(Integer, ForeignKey('storages.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关联到存储池
    storage = relationship("Storage", backref="files")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'size': self.size,
            'type': self.type,
            'storage_id': self.storage_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 