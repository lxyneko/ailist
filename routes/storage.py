from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.storage import Storage
from database import db_session
import json

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/')
def index():
    """存储池列表页面"""
    storages = Storage.query.all()
    return render_template('storage/index.html', storages=storages)

@storage_bp.route('/create', methods=['GET', 'POST'])
def create():
    """创建存储池"""
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        config = {}
        
        if type == 'local':
            config = {
                'path': request.form.get('path')
            }
        elif type == 's3':
            config = {
                'access_key': request.form.get('access_key'),
                'secret_key': request.form.get('secret_key'),
                'bucket': request.form.get('bucket'),
                'region': request.form.get('region')
            }
        
        storage = Storage(
            name=name,
            type=type,
            config=json.dumps(config),
            is_active=False
        )
        
        try:
            db_session.add(storage)
            db_session.commit()
            flash('存储池创建成功！', 'success')
            return redirect(url_for('storage.index'))
        except Exception as e:
            db_session.rollback()
            flash(f'创建存储池失败: {str(e)}', 'error')
    
    return render_template('storage/create.html')

@storage_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """编辑存储池"""
    storage = Storage.query.get_or_404(id)
    
    if request.method == 'POST':
        storage.name = request.form.get('name')
        storage.type = request.form.get('type')
        
        if storage.type == 'local':
            storage.config = json.dumps({
                'path': request.form.get('path')
            })
        elif storage.type == 's3':
            storage.config = json.dumps({
                'access_key': request.form.get('access_key'),
                'secret_key': request.form.get('secret_key'),
                'bucket': request.form.get('bucket'),
                'region': request.form.get('region')
            })
        
        try:
            db_session.commit()
            flash('存储池更新成功！', 'success')
            return redirect(url_for('storage.index'))
        except Exception as e:
            db_session.rollback()
            flash(f'更新存储池失败: {str(e)}', 'error')
    
    try:
        config = json.loads(storage.config)
    except:
        config = {}
    return render_template('storage/edit.html', storage=storage, config=config)

@storage_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """删除存储池"""
    storage = Storage.query.get_or_404(id)
    
    try:
        db_session.delete(storage)
        db_session.commit()
        return jsonify({'success': True, 'message': '存储池删除成功'})
    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'message': f'删除存储池失败: {str(e)}'})

@storage_bp.route('/activate/<int:id>', methods=['POST'])
def activate(id):
    """激活存储池"""
    try:
        # 先将所有存储池设置为非激活状态
        Storage.query.update({Storage.is_active: False})
        db_session.commit()
        
        # 激活指定的存储池
        storage = Storage.query.get_or_404(id)
        storage.is_active = True
        db_session.commit()
        
        return jsonify({'success': True, 'message': '存储池激活成功'})
    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'message': f'激活存储池失败: {str(e)}'}) 