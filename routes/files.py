from flask import Blueprint, request, jsonify, send_file, render_template, redirect, url_for, flash
from models.file import File
from models.storage import Storage
from database import db_session
import os
import json
import boto3
from werkzeug.utils import secure_filename
import mimetypes
from sqlalchemy import or_, and_
from datetime import datetime
import humanize

files_bp = Blueprint('files', __name__)

def get_storage_client(storage):
    """根据存储池类型获取对应的存储客户端"""
    config = json.loads(storage.config)
    if storage.type == 'local':
        return LocalStorage(config)
    elif storage.type == 's3':
        return S3Storage(config)
    raise ValueError(f'不支持的存储类型: {storage.type}')

class LocalStorage:
    def __init__(self, config):
        self.base_path = config.get('path', '')
    
    def get_file_path(self, filename):
        return os.path.join(self.base_path, filename)
    
    def get_file(self, filename):
        file_path = filename # filename here is already the full path
        if os.path.exists(file_path):
            return file_path
        return None

    def save_file(self, file_obj, filename):
        # 确保目录存在
        os.makedirs(self.base_path, exist_ok=True)
        file_path = os.path.join(self.base_path, filename)
        file_obj.save(file_path)
        return file_path

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

class S3Storage:
    def __init__(self, config):
        self.bucket = config.get('bucket')
        self.region = config.get('region')
        self.access_key = config.get('access_key')
        self.secret_key = config.get('secret_key')
    
    def get_file(self, filename):
        import boto3
        from botocore.exceptions import ClientError
        
        try:
            s3 = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            
            # 生成预签名URL
            url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': filename
                },
                ExpiresIn=3600  # URL有效期1小时
            )
            return url
        except ClientError as e:
            print(f"Error getting file from S3: {e}")
            return None

    def save_file(self, file_obj, filename):
        import boto3
        
        s3 = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        s3.upload_fileobj(file_obj, self.bucket, filename)
        return f"s3://{self.bucket}/{filename}"

    def delete_file(self, file_path):
        import boto3

        s3 = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        # 解析 S3 路径，获取 bucket 和 key
        if file_path.startswith('s3://'):
            path_parts = file_path[len('s3://'):].split('/', 1)
            bucket_name = path_parts[0]
            key = path_parts[1] if len(path_parts) > 1 else ''
        else:
            # 如果不是 s3:// 开头，则假定为默认 bucket 的 key
            bucket_name = self.bucket
            key = file_path

        s3.delete_object(Bucket=bucket_name, Key=key)
        return True

@files_bp.route('/')
def index():
    """文件列表页面"""
    # 获取搜索参数
    search_query = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    size_from = request.args.get('size_from', '')
    size_to = request.args.get('size_to', '')
    size_unit = request.args.get('size_unit', 'B')
    file_type = request.args.get('file_type', '')
    
    # 获取当前活跃的存储池
    active_pool = Storage.query.filter_by(is_active=True).first()
    if not active_pool:
        flash('请先配置存储池', 'error')
        return redirect(url_for('storage.index'))

    # 获取所有存储池
    all_storages = db_session.query(Storage).all()
    
    # 构建查询
    query = File.query.filter_by(storage_id=active_pool.id)
    
    # 应用搜索条件
    if search_query:
        query = query.filter(
            or_(
                File.name.ilike(f'%{search_query}%'),
                File.type.ilike(f'%{search_query}%')
            )
        )
    
    # 应用日期范围过滤
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(File.created_at >= date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # 将日期设置为当天的最后一刻
            date_to = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(File.created_at <= date_to)
        except ValueError:
            pass
    
    # 应用文件大小过滤
    if size_from or size_to:
        # 将大小转换为字节
        def convert_to_bytes(size, unit):
            if not size:
                return None
            size = float(size)
            units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            return size * units.get(unit, 1)
        
        size_from_bytes = convert_to_bytes(size_from, size_unit)
        size_to_bytes = convert_to_bytes(size_to, size_unit)
        
        if size_from_bytes is not None:
            query = query.filter(File.size >= size_from_bytes)
        if size_to_bytes is not None:
            query = query.filter(File.size <= size_to_bytes)
    
    # 应用文件类型过滤
    if file_type:
        type_mapping = {
            'image': ['image/'],
            'document': ['application/vnd.openxmlformats-officedocument.wordprocessingml', 'application/msword'],
            'spreadsheet': ['application/vnd.openxmlformats-officedocument.spreadsheetml', 'application/vnd.ms-excel'],
            'presentation': ['application/vnd.openxmlformats-officedocument.presentationml', 'application/vnd.ms-powerpoint']
        }
        
        if file_type in type_mapping:
            type_filters = [File.type.like(f'{prefix}%') for prefix in type_mapping[file_type]]
            query = query.filter(or_(*type_filters))
    
    # 按上传时间倒序排序
    files = query.order_by(File.created_at.desc()).all()
    
    return render_template('files/index.html',
                         files=files,
                         search_query=search_query,
                         date_from=date_from,
                         date_to=date_to,
                         size_from=size_from,
                         size_to=size_to,
                         size_unit=size_unit,
                         file_type=file_type,
                         active_pool=active_pool,
                         all_storages=all_storages)

@files_bp.route('/api/files', methods=['GET'])
def list_files():
    """获取当前存储池的文件列表（API）"""
    # 获取当前活动的存储池
    storage = db_session.query(Storage).filter_by(is_active=1).first()
    if not storage:
        return jsonify({'error': '没有活动的存储池'}), 404
    
    # 获取该存储池下的所有文件
    files = db_session.query(File).filter_by(storage_id=storage.id).all()
    return jsonify([file.to_dict() for file in files])

@files_bp.route('/api/files/upload', methods=['POST'])
def upload_file():
    """上传文件到当前存储池"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 获取当前活动的存储池
    storage = db_session.query(Storage).filter_by(is_active=1).first()
    if not storage:
        return jsonify({'error': '没有活动的存储池'}), 404
    
    try:
        # 获取存储客户端
        storage_client = get_storage_client(storage)
        
        # 净化文件名
        secured_filename = secure_filename(file.filename)

        file_size = 0
        file_path = ""

        if storage.type == 'local':
            file_path = storage_client.save_file(file, secured_filename)
            file_size = os.path.getsize(file_path) # 获取实际文件大小
        elif storage.type == 's3':
            file_path = storage_client.save_file(file, secured_filename)
            file_size = file.content_length # 对于 S3，使用 content_length
        else:
            flash('不支持的存储类型', 'error')
            return jsonify({'error': '不支持的存储类型'}), 400
        
        # 创建文件记录
        file_record = File(
            name=secured_filename,
            original_name=file.filename,
            size=file_size, 
            type=mimetypes.guess_type(secured_filename)[0] or 'application/octet-stream',
            storage_id=storage.id,
            path=file_path
        )
        
        db_session.add(file_record)
        db_session.commit()
        
        flash('文件上传成功！', 'success')
        return redirect(url_for('files.index'))
    
    except Exception as e:
        flash(f'文件上传失败: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500

@files_bp.route('/api/files/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """下载文件"""
    # 获取当前活动的存储池
    storage = db_session.query(Storage).filter_by(is_active=1).first()
    if not storage:
        return jsonify({'error': '没有活动的存储池'}), 404
    
    # 查找文件记录
    file_record = db_session.query(File).filter_by(
        storage_id=storage.id,
        id=file_id
    ).first()
    
    if not file_record:
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        # 获取存储客户端
        storage_client = get_storage_client(storage)
        
        # 获取文件
        return storage_client.get_file(file_record.path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    # 获取当前活动的存储池
    storage = db_session.query(Storage).filter_by(is_active=1).first()
    if not storage:
        return jsonify({'error': '没有活动的存储池'}), 404
    
    # 查找文件记录
    file_record = db_session.query(File).filter_by(
        storage_id=storage.id,
        id=file_id
    ).first()
    
    if not file_record:
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        # 获取存储客户端
        storage_client = get_storage_client(storage)
        
        # 删除文件
        storage_client.delete_file(file_record.path)
        
        # 删除文件记录
        db_session.delete(file_record)
        db_session.commit()
        
        flash('文件删除成功！', 'success')
        return jsonify({'message': '文件已删除'})
    
    except Exception as e:
        flash(f'文件删除失败: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500 