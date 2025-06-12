from typing import Dict, Type
from .local import LocalStorage
from .base import Storage

class StorageFactory:
    _storage_types: Dict[str, Type[Storage]] = {
        "local": LocalStorage
    }
    
    @classmethod
    def create_storage(cls, storage_type: str, **kwargs) -> Storage:
        """创建存储实例"""
        if storage_type not in cls._storage_types:
            raise ValueError(f"不支持的存储类型: {storage_type}")
            
        return cls._storage_types[storage_type](**kwargs) 