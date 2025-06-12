from flask import Blueprint, request, jsonify, send_file
from models.file import File
from models.storage import Storage
from database import db_session
import os
import json
import boto3
from werkzeug.utils import secure_filename
import mimetypes

files_bp = Blueprint('files', __name__)

def get_storage_client(storage):
    """根据存储池类型获取对应的存储客户端"""
    config = json.loads(storage.config)
    if storage.type == 'local':
        return LocalStorage(config['path'])
    elif storage.type == 's3':
        return S3Storage(
            access_key=config['access_key'],
            secret_key=config['secret_key'],
            bucket=config['bucket'],
            region=config['region']
        )
    raise ValueError(f'不支持的存储类型: {storage.type}')

class LocalStorage:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save_file(self, file, filename):
        file_path = os.path.join(self.base_path, filename)
        file.save(file_path)
        return file_path
    
    def get_file(self, file_path):
        return send_file(file_path)
    
    def delete_file(self, file_path):
        os.remove(file_path)

class S3Storage:
    def __init__(self, access_key, secret_key, bucket, region):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        self.bucket = bucket
    
    def save_file(self, file, filename):
        self.s3.upload_fileobj(file, self.bucket, filename)
        return filename
    
    def get_file(self, file_path):
        response = self.s3.get_object(Bucket=self.bucket, Key=file_path)
        return send_file(
            response['Body'],
            mimetype=response['ContentType'],
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    
    def delete_file(self, file_path):
        self.s3.delete_object(Bucket=self.bucket, Key=file_path)

@files_bp.route('/api/files', methods=['GET'])
def list_files():
    """获取当前存储池的文件列表"""
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
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = storage_client.save_file(file, filename)
        
        # 创建文件记录
        file_record = File(
            name=filename,
            path=file_path,
            size=os.path.getsize(file_path) if storage.type == 'local' else 0,  # S3 文件大小暂时设为 0
            type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
            storage_id=storage.id
        )
        
        db_session.add(file_record)
        db_session.commit()
        
        return jsonify(file_record.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/api/files/<path:filename>', methods=['GET'])
def download_file(filename):
    """下载文件"""
    # 获取当前活动的存储池
    storage = db_session.query(Storage).filter_by(is_active=1).first()
    if not storage:
        return jsonify({'error': '没有活动的存储池'}), 404
    
    # 查找文件记录
    file_record = db_session.query(File).filter_by(
        storage_id=storage.id,
        name=filename
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

@files_bp.route('/api/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    """删除文件"""
    # 获取当前活动的存储池
    storage = db_session.query(Storage).filter_by(is_active=1).first()
    if not storage:
        return jsonify({'error': '没有活动的存储池'}), 404
    
    # 查找文件记录
    file_record = db_session.query(File).filter_by(
        storage_id=storage.id,
        name=filename
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
        
        return jsonify({'message': '文件已删除'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 