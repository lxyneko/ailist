from flask import Blueprint, jsonify, request, render_template
from services.ai_service import AIService
from models.file import File
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
    return {}

def save_config(config):
    """保存AI配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

@ai_bp.route('/config', methods=['GET'])
def config():
    """AI配置页面"""
    config = load_config()
    return render_template('ai/config.html', config=config)

@ai_bp.route('/api/config', methods=['GET'])
def get_config():
    """获取AI配置"""
    config = load_config()
    return jsonify(config)

@ai_bp.route('/api/config', methods=['POST'])
def update_config():
    """更新AI配置"""
    config = request.json
    save_config(config)
    return jsonify({'message': '配置已更新'})

@ai_bp.route('/analyze/<int:file_id>', methods=['POST'])
def analyze_file(file_id):
    """分析指定文件的内容"""
    file = db_session.query(File).get(file_id)
    if not file:
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        with open(file.path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = ai_service.analyze_file_content(content, file_id)
        if analysis:
            return jsonify({
                'summary': analysis.content_summary,
                'tags': analysis.suggested_tags,
                'sentiment_score': analysis.sentiment_score
            })
        return jsonify({'error': '分析失败'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analysis/<int:file_id>', methods=['GET'])
def get_analysis(file_id):
    """获取文件的分析结果"""
    analysis = ai_service.get_file_analysis(file_id)
    if analysis:
        return jsonify({
            'summary': analysis.content_summary,
            'tags': analysis.suggested_tags,
            'sentiment_score': analysis.sentiment_score
        })
    return jsonify({'error': '未找到分析结果'}), 404

@ai_bp.route('/search', methods=['GET'])
def search_files():
    """搜索相似文件"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '请提供搜索关键词'}), 400
    
    results = ai_service.search_similar_files(query)
    return jsonify({'results': results}) 