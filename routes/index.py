from flask import Blueprint, render_template
from models.file import File
from models.storage import Storage
from database import db_session

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    """首页"""
    # 获取文件统计信息
    total_files = File.query.count()
    total_storage = Storage.query.count()
    active_storage = Storage.query.filter_by(is_active=True).first()
    
    # 获取最近上传的文件
    recent_files = File.query.order_by(File.created_at.desc()).limit(5).all()
    
    # 获取存储池使用情况
    storage_usage = {}
    if active_storage:
        storage_usage = {
            'name': active_storage.name,
            'type': active_storage.type,
            'files_count': File.query.filter_by(storage_id=active_storage.id).count()
        }
    
    return render_template('index.html',
                         total_files=total_files,
                         total_storage=total_storage,
                         recent_files=recent_files,
                         storage_usage=storage_usage) 