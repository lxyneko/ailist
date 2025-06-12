from pathlib import Path
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from .base import Storage
from ..models import File

class LocalStorage(Storage):
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
    async def list_files(self, path: str = "/") -> List[File]:
        """列出指定目录下的所有文件和文件夹"""
        target_path = self.base_path / path.lstrip("/")
        if not target_path.exists():
            return []
            
        files = []
        for item in target_path.iterdir():
            if item.name.startswith(".") or item.name in ["venv", "node_modules", "__pycache__"]:
                continue
                
            stat = item.stat()
            files.append(File(
                id=len(files) + 1,
                name=item.name,
                type="directory" if item.is_dir() else "file",
                size=stat.st_size,
                path=str(item.relative_to(self.base_path)),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
            ))
            
        return files
        
    async def get_file(self, path: str) -> Optional[File]:
        """获取文件信息"""
        target_path = self.base_path / path.lstrip("/")
        if not target_path.exists():
            return None
            
        stat = target_path.stat()
        return File(
            name=target_path.name,
            type="directory" if target_path.is_dir() else "file",
            size=stat.st_size,
            path=str(target_path.relative_to(self.base_path)),
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )
        
    async def upload_file(self, path: str, file_data: bytes) -> File:
        """上传文件"""
        target_path = self.base_path / path.lstrip("/")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, "wb") as f:
            f.write(file_data)
            
        return await self.get_file(path)
        
    async def download_file(self, path: str) -> bytes:
        """下载文件"""
        target_path = self.base_path / path.lstrip("/")
        if not target_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
            
        with open(target_path, "rb") as f:
            return f.read()
            
    async def delete_file(self, path: str) -> bool:
        """删除文件或目录"""
        target_path = self.base_path / path.lstrip("/")
        if not target_path.exists():
            return False
            
        if target_path.is_dir():
            target_path.rmdir()
        else:
            target_path.unlink()
        return True
        
    async def create_directory(self, path: str) -> bool:
        """创建目录"""
        target_path = self.base_path / path.lstrip("/")
        if target_path.exists():
            return False
            
        target_path.mkdir(parents=True)
        return True
        
    async def move_file(self, src_path: str, dst_path: str) -> bool:
        """移动文件"""
        src = self.base_path / src_path.lstrip("/")
        dst = self.base_path / dst_path.lstrip("/")
        
        if not src.exists():
            return False
            
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        return True
        
    async def copy_file(self, src_path: str, dst_path: str) -> bool:
        """复制文件"""
        src = self.base_path / src_path.lstrip("/")
        dst = self.base_path / dst_path.lstrip("/")
        
        if not src.exists():
            return False
            
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if src.is_dir():
            import shutil
            shutil.copytree(src, dst)
        else:
            import shutil
            shutil.copy2(src, dst)
            
        return True 