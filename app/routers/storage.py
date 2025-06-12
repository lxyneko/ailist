from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from typing import List, Optional
from pydantic import BaseModel
from ..services.storage import storage_service
from ..models import File
from ..models.storage import Storage
from ..auth import get_current_user
from ..schemas.storage import Storage, StorageCreate, StorageUpdate
from ..schemas.file import File
from fastapi.responses import Response
import json
import os

router = APIRouter(prefix="/api")

class WebDAVConfig(BaseModel):
    url: str
    username: str
    password: str
    path: str = "/"

class S3Config(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    region: str = "us-east-1"
    path: str = "/"

class LocalConfig(BaseModel):
    path: str

class StorageConfig(BaseModel):
    type: str
    path: Optional[str] = None
    webdav: Optional[WebDAVConfig] = None

CONFIG_FILE = "storage_config.json"

def load_config() -> StorageConfig:
    if not os.path.exists(CONFIG_FILE):
        return StorageConfig(type="local", path=".")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return StorageConfig(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载配置失败: {str(e)}")

def save_config(config: StorageConfig):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

@router.get("/storages", response_model=List[Storage])
async def list_storages(current_user: str = Depends(get_current_user)):
    """列出所有存储后端"""
    return await storage_service.list_storages()

@router.post("/storages", response_model=Storage)
async def create_storage(
    storage: StorageCreate,
    current_user: str = Depends(get_current_user)
):
    """创建新的存储后端"""
    return await storage_service.add_storage(
        name=storage.name,
        type=storage.type,
        config=storage.config
    )

@router.get("/storages/{storage_id}", response_model=Storage)
async def get_storage(
    storage_id: int,
    current_user: str = Depends(get_current_user)
):
    """获取存储后端信息"""
    storage = await storage_service.get_storage_info(storage_id)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="存储后端不存在"
        )
    return storage

@router.delete("/storages/{storage_id}")
async def delete_storage(
    storage_id: int,
    current_user: str = Depends(get_current_user)
):
    """删除存储后端"""
    if not await storage_service.remove_storage(storage_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="存储后端不存在"
        )
    return {"message": "存储后端已删除"}

@router.get("/storages/{storage_id}/files", response_model=List[File])
async def list_files(
    storage_id: int,
    path: str = "/",
    current_user: str = Depends(get_current_user)
):
    """列出指定存储后端的文件"""
    try:
        return await storage_service.list_files(storage_id, path)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/storages/{storage_id}/files/{path:path}", response_model=File)
async def get_file(
    storage_id: int,
    path: str,
    current_user: str = Depends(get_current_user)
):
    """获取文件信息"""
    try:
        file = await storage_service.get_file(storage_id, path)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        return file
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/storages/{storage_id}/files/{path:path}")
async def upload_file(
    storage_id: int,
    path: str,
    file: UploadFile = FastAPIFile(...),
    current_user: str = Depends(get_current_user)
):
    """上传文件"""
    try:
        file_data = await file.read()
        return await storage_service.upload_file(storage_id, path, file_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/storages/{storage_id}/files/{path:path}/download")
async def download_file(
    storage_id: int,
    path: str,
    current_user: str = Depends(get_current_user)
):
    """下载文件"""
    try:
        file_data = await storage_service.download_file(storage_id, path)
        return Response(
            content=file_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{path.split("/")[-1]}"'
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/storages/{storage_id}/files/{path:path}")
async def delete_file(
    storage_id: int,
    path: str,
    current_user: str = Depends(get_current_user)
):
    """删除文件"""
    try:
        if not await storage_service.delete_file(storage_id, path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        return {"message": "文件已删除"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/storages/{storage_id}/directories/{path:path}")
async def create_directory(
    storage_id: int,
    path: str,
    current_user: str = Depends(get_current_user)
):
    """创建目录"""
    try:
        if not await storage_service.create_directory(storage_id, path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建目录失败"
            )
        return {"message": "目录已创建"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/storages/{storage_id}/files/{path:path}/move")
async def move_file(
    storage_id: int,
    path: str,
    dst_path: str,
    current_user: str = Depends(get_current_user)
):
    """移动文件"""
    try:
        if not await storage_service.move_file(storage_id, path, dst_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="移动文件失败"
            )
        return {"message": "文件已移动"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/storages/{storage_id}/files/{path:path}/copy")
async def copy_file(
    storage_id: int,
    path: str,
    dst_path: str,
    current_user: str = Depends(get_current_user)
):
    """复制文件"""
    try:
        if not await storage_service.copy_file(storage_id, path, dst_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="复制文件失败"
            )
        return {"message": "文件已复制"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/config")
async def get_storage_config():
    return load_config()

@router.post("/config")
async def update_storage_config(config: StorageConfig):
    save_config(config)
    return {"message": "配置已保存"} 