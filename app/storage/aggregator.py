from typing import List, Dict, Optional
from .base import StorageBackend
from ..models import File, Storage
from sqlalchemy.orm import Session

class StorageAggregator:
    def __init__(self, db: Session):
        self.db = db
        self.storages: Dict[int, StorageBackend] = {}

    async def get_storage(self, storage_id: int) -> Optional[StorageBackend]:
        """获取存储后端实例"""
        if storage_id not in self.storages:
            storage = self.db.query(Storage).filter(Storage.id == storage_id).first()
            if not storage:
                return None
            
            # 根据存储类型创建对应的后端实例
            if storage.type == "local":
                from .local import LocalStorage
                self.storages[storage_id] = LocalStorage(storage.config)
            elif storage.type == "s3":
                from .s3 import S3Storage
                self.storages[storage_id] = S3Storage(storage.config)
            elif storage.type == "webdav":
                from .webdav import WebDAVStorage
                self.storages[storage_id] = WebDAVStorage(storage.config)
            # 可以添加更多存储类型
            
        return self.storages[storage_id]

    async def list_all_files(self, path: str = "/") -> List[File]:
        """列出所有存储中的文件"""
        all_files = []
        storages = self.db.query(Storage).all()
        
        for storage in storages:
            backend = await self.get_storage(storage.id)
            if backend:
                try:
                    files = await backend.list_files(path)
                    for file in files:
                        file.storage_id = storage.id
                        file.storage_name = storage.name
                    all_files.extend(files)
                except Exception as e:
                    print(f"Error listing files from storage {storage.name}: {e}")
        
        return all_files

    async def search_files(self, query: str) -> List[File]:
        """在所有存储中搜索文件"""
        all_files = []
        storages = self.db.query(Storage).all()
        
        for storage in storages:
            backend = await self.get_storage(storage.id)
            if backend:
                try:
                    files = await backend.list_files("/")
                    for file in files:
                        if query.lower() in file.name.lower():
                            file.storage_id = storage.id
                            file.storage_name = storage.name
                            all_files.append(file)
                except Exception as e:
                    print(f"Error searching files in storage {storage.name}: {e}")
        
        return all_files

    async def get_file(self, storage_id: int, path: str) -> Optional[File]:
        """获取指定存储中的文件"""
        backend = await self.get_storage(storage_id)
        if backend:
            return await backend.get_file(path)
        return None

    async def upload_file(self, storage_id: int, path: str, file_data: bytes) -> Optional[File]:
        """上传文件到指定存储"""
        backend = await self.get_storage(storage_id)
        if backend:
            return await backend.upload_file(path, file_data)
        return None

    async def download_file(self, storage_id: int, path: str) -> Optional[bytes]:
        """从指定存储下载文件"""
        backend = await self.get_storage(storage_id)
        if backend:
            return await backend.download_file(path)
        return None

    async def delete_file(self, storage_id: int, path: str) -> bool:
        """删除指定存储中的文件"""
        backend = await self.get_storage(storage_id)
        if backend:
            return await backend.delete_file(path)
        return False

    async def move_file(self, src_storage_id: int, src_path: str, 
                       dst_storage_id: int, dst_path: str) -> bool:
        """在不同存储间移动文件"""
        src_backend = await self.get_storage(src_storage_id)
        dst_backend = await self.get_storage(dst_storage_id)
        
        if src_backend and dst_backend:
            try:
                # 下载源文件
                file_data = await src_backend.download_file(src_path)
                if not file_data:
                    return False
                
                # 上传到目标存储
                await dst_backend.upload_file(dst_path, file_data)
                
                # 删除源文件
                await src_backend.delete_file(src_path)
                return True
            except Exception as e:
                print(f"Error moving file: {e}")
                return False
        return False

    async def copy_file(self, src_storage_id: int, src_path: str,
                       dst_storage_id: int, dst_path: str) -> bool:
        """在不同存储间复制文件"""
        src_backend = await self.get_storage(src_storage_id)
        dst_backend = await self.get_storage(dst_storage_id)
        
        if src_backend and dst_backend:
            try:
                # 下载源文件
                file_data = await src_backend.download_file(src_path)
                if not file_data:
                    return False
                
                # 上传到目标存储
                await dst_backend.upload_file(dst_path, file_data)
                return True
            except Exception as e:
                print(f"Error copying file: {e}")
                return False
        return False 