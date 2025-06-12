from flask import Blueprint, request, jsonify
from models.storage import Storage
from database import db_session
import json

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/api/storage/list', methods=['GET'])
def list_storages():
    """获取所有存储池列表"""
    storages = db_session.query(Storage).all()
    return jsonify([storage.to_dict() for storage in storages])

@storage_bp.route('/api/storage/config', methods=['GET', 'POST'])
def storage_config():
    """获取或设置当前存储池配置"""
    if request.method == 'GET':
        # 获取当前活动的存储池
        storage = db_session.query(Storage).filter_by(is_active=1).first()
        if not storage:
            return jsonify({'error': '没有活动的存储池'}), 404
        return jsonify(storage.to_dict())
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['name', 'type', 'config']
        if not all(field in data for field in required_fields):
            return jsonify({'error': '缺少必要字段'}), 400
        
        # 验证存储类型
        if data['type'] not in ['local', 's3']:
            return jsonify({'error': '不支持的存储类型'}), 400
        
        # 验证配置
        try:
            config = json.loads(data['config'])
            if data['type'] == 'local':
                if 'path' not in config:
                    return jsonify({'error': '本地存储需要指定路径'}), 400
            elif data['type'] == 's3':
                required_s3_fields = ['access_key', 'secret_key', 'bucket', 'region']
                if not all(field in config for field in required_s3_fields):
                    return jsonify({'error': 'S3存储需要指定所有必要字段'}), 400
        except json.JSONDecodeError:
            return jsonify({'error': '配置格式错误'}), 400
        
        # 创建新的存储池
        storage = Storage(
            name=data['name'],
            type=data['type'],
            config=data['config'],
            is_active=1  # 新创建的存储池设为活动状态
        )
        
        # 将其他存储池设为非活动
        db_session.query(Storage).update({'is_active': 0})
        
        # 保存新存储池
        db_session.add(storage)
        db_session.commit()
        
        return jsonify(storage.to_dict())

@storage_bp.route('/api/storage/switch/<int:storage_id>', methods=['POST'])
def switch_storage(storage_id):
    """切换到指定的存储池"""
    # 查找目标存储池
    storage = db_session.query(Storage).get(storage_id)
    if not storage:
        return jsonify({'error': '存储池不存在'}), 404
    
    # 将所有存储池设为非活动
    db_session.query(Storage).update({'is_active': 0})
    
    # 将目标存储池设为活动
    storage.is_active = 1
    db_session.commit()
    
    return jsonify(storage.to_dict()) 