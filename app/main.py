from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import json
from werkzeug.utils import secure_filename
import mimetypes

from app.database import get_db
from app.models.storage import Storage
from app.models.file import File

app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 存储客户端工厂
def get_storage_client(storage: Storage):
    """根据存储池类型获取对应的存储客户端"""
    config = json.loads(storage.config)
    if storage.type == 'local':
        return LocalStorage(config['path'])
    raise ValueError(f'不支持的存储类型: {storage.type}')

class LocalStorage:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save_file(self, file: UploadFile, filename: str) -> str:
        file_path = os.path.join(self.base_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())
        return file_path
    
    def get_file(self, file_path: str) -> FileResponse:
        return FileResponse(file_path)
    
    def delete_file(self, file_path: str):
        os.remove(file_path)

# 存储池相关路由
@app.get("/api/storage/list")
def list_storages(db: Session = Depends(get_db)):
    """获取所有存储池列表"""
    storages = db.query(Storage).all()
    return [storage.to_dict() for storage in storages]

@app.get("/api/storage/config")
def get_storage_config(db: Session = Depends(get_db)):
    """获取当前存储池配置"""
    storage = db.query(Storage).filter_by(is_active=1).first()
    if not storage:
        raise HTTPException(status_code=404, detail="没有活动的存储池")
    return storage.to_dict()

@app.post("/api/storage/config")
def create_storage(data: dict, db: Session = Depends(get_db)):
    """创建新的存储池"""
    # 验证必要字段
    required_fields = ['name', 'type', 'config']
    if not all(field in data for field in required_fields):
        raise HTTPException(status_code=400, detail="缺少必要字段")
    
    # 验证存储类型
    if data['type'] != 'local':
        raise HTTPException(status_code=400, detail="目前只支持本地存储")
    
    # 验证配置
    try:
        config = json.loads(data['config'])
        if 'path' not in config:
            raise HTTPException(status_code=400, detail="本地存储需要指定路径")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="配置格式错误")
    
    # 创建新的存储池
    storage = Storage(
        name=data['name'],
        type=data['type'],
        config=data['config'],
        is_active=1
    )
    
    # 将其他存储池设为非活动
    db.query(Storage).update({'is_active': 0})
    
    # 保存新存储池
    db.add(storage)
    db.commit()
    db.refresh(storage)
    
    return storage.to_dict()

@app.post("/api/storage/switch/{storage_id}")
def switch_storage(storage_id: int, db: Session = Depends(get_db)):
    """切换到指定的存储池"""
    storage = db.query(Storage).get(storage_id)
    if not storage:
        raise HTTPException(status_code=404, detail="存储池不存在")
    
    # 将所有存储池设为非活动
    db.query(Storage).update({'is_active': 0})
    
    # 将目标存储池设为活动
    storage.is_active = 1
    db.commit()
    
    return storage.to_dict()

# 文件相关路由
@app.get("/api/files")
def list_files(db: Session = Depends(get_db)):
    """获取当前存储池的文件列表"""
    storage = db.query(Storage).filter_by(is_active=1).first()
    if not storage:
        raise HTTPException(status_code=404, detail="没有活动的存储池")
    
    files = db.query(File).filter_by(storage_id=storage.id).all()
    return [file.to_dict() for file in files]

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传文件到当前存储池"""
    storage = db.query(Storage).filter_by(is_active=1).first()
    if not storage:
        raise HTTPException(status_code=404, detail="没有活动的存储池")
    
    try:
        # 获取存储客户端
        storage_client = get_storage_client(storage)
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = storage_client.save_file(file, filename)
        
        # 创建文件记录
        file_record = File(
            name=filename,
            path=file_path,
            size=os.path.getsize(file_path),
            type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
            storage_id=storage.id
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        return file_record.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{filename}")
def download_file(filename: str, db: Session = Depends(get_db)):
    """下载文件"""
    storage = db.query(Storage).filter_by(is_active=1).first()
    if not storage:
        raise HTTPException(status_code=404, detail="没有活动的存储池")
    
    file_record = db.query(File).filter_by(
        storage_id=storage.id,
        name=filename
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        storage_client = get_storage_client(storage)
        return storage_client.get_file(file_record.path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{filename}")
def delete_file(filename: str, db: Session = Depends(get_db)):
    """删除文件"""
    storage = db.query(Storage).filter_by(is_active=1).first()
    if not storage:
        raise HTTPException(status_code=404, detail="没有活动的存储池")
    
    file_record = db.query(File).filter_by(
        storage_id=storage.id,
        name=filename
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        storage_client = get_storage_client(storage)
        storage_client.delete_file(file_record.path)
        
        db.delete(file_record)
        db.commit()
        
        return {"message": "文件已删除"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 