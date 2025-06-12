from typing import List, Optional, Dict
import json
from ..models import File as FileModel, Storage as StorageModel
from ..storage.factory import StorageFactory
from ..database import get_db
from ..storage.base import Storage as StorageBase
from ..schemas.storage import Storage, StorageCreate
from ..schemas.file import File

class StorageService:
    def __init__(self):
        self._storages: Dict[int, StorageBase] = {}

    async def get_storage(self, storage_id: int) -> StorageBase:
        """获取存储后端实例"""
        if storage_id not in self._storages:
            db = next(get_db())
            storage = db.query(StorageModel).filter(StorageModel.id == storage_id).first()
            if not storage:
                raise ValueError(f"存储后端不存在: {storage_id}")
                
            self._storages[storage_id] = StorageFactory.create(
                storage.type,
                json.loads(storage.config)
            )
            
        return self._storages[storage_id]

    async def list_files(self, storage_id: int, path: str = "/") -> List[File]:
        """列出指定存储后端的文件"""
        storage = await self.get_storage(storage_id)
        files = await storage.list_files(path)
        return [File.from_orm(file) for file in files]

    async def get_file(self, storage_id: int, path: str) -> Optional[File]:
        """获取文件信息"""
        storage = await self.get_storage(storage_id)
        file = await storage.get_file(path)
        if not file:
            return None
        return File.from_orm(file)

    async def upload_file(self, storage_id: int, path: str, file_data: bytes) -> File:
        """上传文件"""
        storage = await self.get_storage(storage_id)
        file = await storage.upload_file(path, file_data)
        return File.from_orm(file)

    async def download_file(self, storage_id: int, path: str) -> bytes:
        """下载文件"""
        storage = await self.get_storage(storage_id)
        return await storage.download_file(path)

    async def delete_file(self, storage_id: int, path: str) -> bool:
        """删除文件"""
        storage = await self.get_storage(storage_id)
        return await storage.delete_file(path)

    async def create_directory(self, storage_id: int, path: str) -> bool:
        """创建目录"""
        storage = await self.get_storage(storage_id)
        return await storage.create_directory(path)

    async def move_file(self, storage_id: int, src_path: str, dst_path: str) -> bool:
        """移动文件"""
        storage = await self.get_storage(storage_id)
        return await storage.move_file(src_path, dst_path)

    async def copy_file(self, storage_id: int, src_path: str, dst_path: str) -> bool:
        """复制文件"""
        storage = await self.get_storage(storage_id)
        return await storage.copy_file(src_path, dst_path)

    async def add_storage(self, name: str, type: str, config: str) -> Storage:
        """添加新的存储后端"""
        db = next(get_db())
        storage = StorageModel(
            name=name,
            type=type,
            config=config
        )
        db.add(storage)
        db.commit()
        db.refresh(storage)
        return Storage.from_orm(storage)

    async def remove_storage(self, storage_id: int) -> bool:
        """删除存储后端"""
        db = next(get_db())
        storage = db.query(StorageModel).filter(StorageModel.id == storage_id).first()
        if not storage:
            return False
            
        if storage_id in self._storages:
            del self._storages[storage_id]
            
        db.delete(storage)
        db.commit()
        return True

    async def list_storages(self) -> List[Storage]:
        """列出所有存储后端"""
        db = next(get_db())
        storages = db.query(StorageModel).all()
        return [Storage.from_orm(storage) for storage in storages]

    async def get_storage_info(self, storage_id: int) -> Optional[Storage]:
        """获取存储后端信息"""
        db = next(get_db())
        storage = db.query(StorageModel).filter(StorageModel.id == storage_id).first()
        if not storage:
            return None
        return Storage.from_orm(storage)

storage_service = StorageService() 