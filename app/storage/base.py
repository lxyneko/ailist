from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models import File

class Storage(ABC):
    @abstractmethod
    async def list_files(self, path: str = "/") -> List[File]:
        """列出指定路径下的文件"""
        pass

    @abstractmethod
    async def get_file(self, path: str) -> Optional[File]:
        """获取文件信息"""
        pass

    @abstractmethod
    async def upload_file(self, path: str, file_data: bytes) -> File:
        """上传文件"""
        pass

    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """下载文件"""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """删除文件"""
        pass

    @abstractmethod
    async def create_directory(self, path: str) -> bool:
        """创建目录"""
        pass

    @abstractmethod
    async def move_file(self, src_path: str, dst_path: str) -> bool:
        """移动文件"""
        pass

    @abstractmethod
    async def copy_file(self, src_path: str, dst_path: str) -> bool:
        """复制文件"""
        pass 