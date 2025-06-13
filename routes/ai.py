from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for, current_app
from services.ai_service import AIService
from models.file import File
from models.storage import Storage
from database import db_session
import os
import json

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()

CONFIG_FILE = 'ai_config.json'

def load_config():
    """加载AI配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'apiKey': '',
        'temperature': 0.7
    }

def save_config(config):
    """保存AI配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

@ai_bp.route('/config', methods=['GET', 'POST'])
def config():
    """AI配置页面"""
    if request.method == 'POST':
        config = {
            'apiKey': request.form.get('apiKey'),
            'temperature': float(request.form.get('temperature', 0.7))
        }
        with open('ai_config.json', 'w') as f:
            json.dump(config, f)
        return jsonify({'success': True})
    
    # 加载配置
    config = ai_service.load_config()
    return render_template('ai/config.html', config=config)

@ai_bp.route('/api/config', methods=['GET'])
def get_config():
    """获取AI配置"""
    config = ai_service.load_config()
    return jsonify(config)

@ai_bp.route('/api/config', methods=['POST'])
def update_config():
    """更新AI配置"""
    config = request.json
    with open('ai_config.json', 'w') as f:
        json.dump(config, f)
    return jsonify({'success': True})

@ai_bp.route('/api/test-connection', methods=['POST'])
def test_connection():
    """测试AI服务连接"""
    api_key = request.json.get('apiKey')
    if not api_key:
        return jsonify({'success': False, 'message': '请提供API密钥'})
    
    success = ai_service.test_connection(api_key)
    return jsonify({'success': success})

@ai_bp.route('/analysis/<int:file_id>')
def analysis(file_id):
    """文件分析页面"""
    file = db_session.query(File).get(file_id)
    if not file:
        return '文件不存在', 404
    
    # 获取存储池
    storage = db_session.query(Storage).get(file.storage_id)
    if not storage:
        return '存储池不存在', 404
    
    # 获取存储客户端
    storage_client = ai_service.get_storage_client(storage)
    
    try:
        # 获取文件内容
        file_content = storage_client.get_file_content(file.path)
        
        # 获取文件类型
        file_type = file.mime_type or 'text/plain'
        
        # 分析文件内容
        analysis = ai_service.analyze_file_content(file_content, file_id, file_type)
        
        return render_template('ai/analysis.html', 
                             file=file,
                             analysis=analysis)
    except Exception as e:
        current_app.logger.error(f"分析文件时出错: {str(e)}")
        return render_template('ai/analysis.html',
                             file=file,
                             error=str(e))

@ai_bp.route('/search')
def search():
    """智能搜索页面"""
    return render_template('ai/search.html')

@ai_bp.route('/api/search', methods=['POST'])
def api_search():
    """智能搜索API"""
    query = request.json.get('query')
    semantic = request.json.get('semantic', True)
    content = request.json.get('content', False)
    
    if not query:
        return jsonify({'success': False, 'message': '请提供搜索关键词'})
    
    results = ai_service.search_similar_files(query, semantic, content)
    return jsonify({
        'success': True,
        'results': [{
            'id': file.id,
            'name': file.name,
            'type': file.type,
            'size': file.size,
            'created_at': file.created_at.isoformat()
        } for file in results]
    }) 