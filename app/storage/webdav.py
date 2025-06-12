import os
from typing import List, Optional
import json
from webdav3.client import Client
from .base import StorageBackend
from ..models import File

class WebDAVStorage(StorageBackend):
    def __init__(self, config: str):
        self.config = json.loads(config)
        self.client = Client({
            'webdav_hostname': self.config['url'],
            'webdav_login': self.config['username'],
            'webdav_password': self.config['password'],
            'webdav_timeout': 30,
        })

    async def list_files(self, path: str = "/") -> List[File]:
        """列出指定路径下的文件"""
        try:
            # 确保路径以/开头
            path = path if path.startswith('/') else f'/{path}'
            
            # 获取文件列表
            files = self.client.list(path)
            result = []
            
            for file_path in files:
                # 跳过当前目录
                if file_path == path:
                    continue
                    
                # 获取文件信息
                info = self.client.info(file_path)
                is_dir = info.get('type') == 'directory'
                
                # 创建文件对象
                file = File(
                    name=os.path.basename(file_path),
                    path=file_path,
                    type="directory" if is_dir else "file",
                    size=info.get('size', 0)
                )
                result.append(file)
                
            return result
        except Exception as e:
            print(f"Error listing files from WebDAV: {e}")
            return []

    async def get_file(self, path: str) -> Optional[File]:
        """获取文件信息"""
        try:
            # 确保路径以/开头
            path = path if path.startswith('/') else f'/{path}'
            
            # 获取文件信息
            info = self.client.info(path)
            if not info:
                return None
                
            is_dir = info.get('type') == 'directory'
            return File(
                name=os.path.basename(path),
                path=path,
                type="directory" if is_dir else "file",
                size=info.get('size', 0)
            )
        except Exception as e:
            print(f"Error getting file info from WebDAV: {e}")
            return None

    async def upload_file(self, path: str, file_data: bytes) -> File:
        """上传文件"""
        try:
            # 确保路径以/开头
            path = path if path.startswith('/') else f'/{path}'
            
            # 创建临时文件
            temp_path = f"/tmp/{os.path.basename(path)}"
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            
            # 上传文件
            self.client.upload_sync(temp_path, path)
            
            # 删除临时文件
            os.remove(temp_path)
            
            # 返回文件信息
            return await self.get_file(path)
        except Exception as e:
            print(f"Error uploading file to WebDAV: {e}")
            raise

    async def download_file(self, path: str) -> bytes:
        """下载文件"""
        try:
            # 确保路径以/开头
            path = path if path.startswith('/') else f'/{path}'
            
            # 创建临时文件
            temp_path = f"/tmp/{os.path.basename(path)}"
            
            # 下载文件
            self.client.download_sync(path, temp_path)
            
            # 读取文件内容
            with open(temp_path, 'rb') as f:
                content = f.read()
            
            # 删除临时文件
            os.remove(temp_path)
            
            return content
        except Exception as e:
            print(f"Error downloading file from WebDAV: {e}")
            raise

    async def delete_file(self, path: str) -> bool:
        """删除文件"""
        try:
            # 确保路径以/开头
            path = path if path.startswith('/') else f'/{path}'
            
            # 删除文件
            self.client.clean(path)
            return True
        except Exception as e:
            print(f"Error deleting file from WebDAV: {e}")
            return False

    async def create_directory(self, path: str) -> bool:
        """创建目录"""
        try:
            # 确保路径以/开头
            path = path if path.startswith('/') else f'/{path}'
            
            # 创建目录
            self.client.mkdir(path)
            return True
        except Exception as e:
            print(f"Error creating directory in WebDAV: {e}")
            return False

    async def move_file(self, src_path: str, dst_path: str) -> bool:
        """移动文件"""
        try:
            # 确保路径以/开头
            src_path = src_path if src_path.startswith('/') else f'/{src_path}'
            dst_path = dst_path if dst_path.startswith('/') else f'/{dst_path}'
            
            # 移动文件
            self.client.move(src_path, dst_path)
            return True
        except Exception as e:
            print(f"Error moving file in WebDAV: {e}")
            return False

    async def copy_file(self, src_path: str, dst_path: str) -> bool:
        """复制文件"""
        try:
            # 确保路径以/开头
            src_path = src_path if src_path.startswith('/') else f'/{src_path}'
            dst_path = dst_path if dst_path.startswith('/') else f'/{dst_path}'
            
            # 复制文件
            self.client.copy(src_path, dst_path)
            return True
        except Exception as e:
            print(f"Error copying file in WebDAV: {e}")
            return False 