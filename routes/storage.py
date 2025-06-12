from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.storage import Storage
from database import db_session
import json

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/storage')
def index():
    """存储管理页面"""
    storages = db_session.query(Storage).all()
    return render_template('storage/index.html', storages=storages)

@storage_bp.route('/api/storage', methods=['GET'])
def list_storage():
    """获取存储池列表（API）"""
    storages = db_session.query(Storage).all()
    return jsonify([storage.to_dict() for storage in storages])

@storage_bp.route('/api/storage', methods=['POST'])
def add_storage():
    """添加存储池"""
    data = request.form
    
    # 验证必填字段
    if not data.get('name') or not data.get('type'):
        flash('名称和类型是必填项', 'error')
        return redirect(url_for('storage.index'))
    
    # 根据存储类型验证配置
    config = {}
    if data['type'] == 'local':
        if not data.get('path'):
            flash('本地存储需要指定路径', 'error')
            return redirect(url_for('storage.index'))
        config['path'] = data['path']
    elif data['type'] == 's3':
        required_fields = ['access_key', 'secret_key', 'bucket', 'region']
        for field in required_fields:
            if not data.get(field):
                flash(f'S3 存储需要指定 {field}', 'error')
                return redirect(url_for('storage.index'))
        config = {
            'access_key': data['access_key'],
            'secret_key': data['secret_key'],
            'bucket': data['bucket'],
            'region': data['region']
        }
    else:
        flash('不支持的存储类型', 'error')
        return redirect(url_for('storage.index'))
    
    try:
        # 创建存储池
        storage = Storage(
            name=data['name'],
            type=data['type'],
            config=json.dumps(config),
            is_active=0  # 新创建的存储池默认非活动
        )
        
        db_session.add(storage)
        db_session.commit()
        
        flash('存储池添加成功！', 'success')
        return redirect(url_for('storage.index'))
    
    except Exception as e:
        flash(f'添加存储池失败: {str(e)}', 'error')
        return redirect(url_for('storage.index'))

@storage_bp.route('/api/storage/<int:storage_id>/activate', methods=['POST'])
def activate_storage(storage_id):
    """激活存储池"""
    try:
        # 将所有存储池设置为非活动
        db_session.query(Storage).update({Storage.is_active: 0})
        
        # 激活指定的存储池
        storage = db_session.query(Storage).get(storage_id)
        if not storage:
            return jsonify({'error': '存储池不存在'}), 404
        
        storage.is_active = 1
        db_session.commit()
        
        return jsonify(storage.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@storage_bp.route('/api/storage/<int:storage_id>/deactivate', methods=['POST'])
def deactivate_storage(storage_id):
    """停用存储池"""
    try:
        storage = db_session.query(Storage).get(storage_id)
        if not storage:
            return jsonify({'error': '存储池不存在'}), 404
        
        if not storage.is_active:
            return jsonify({'message': '存储池已是非活动状态'}), 200

        storage.is_active = 0
        db_session.commit()
        
        return jsonify(storage.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@storage_bp.route('/api/storage/<int:storage_id>', methods=['DELETE'])
def delete_storage(storage_id):
    """删除存储池"""
    try:
        storage = db_session.query(Storage).get(storage_id)
        if not storage:
            return jsonify({'error': '存储池不存在'}), 404
        
        # 不允许删除活动的存储池
        if storage.is_active:
            return jsonify({'error': '不能删除活动的存储池，请先停用'}), 400
        
        db_session.delete(storage)
        db_session.commit()
        
        return jsonify({'message': '存储池已删除'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 