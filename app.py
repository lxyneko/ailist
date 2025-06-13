from flask import Flask, render_template, send_from_directory
from routes.storage import storage_bp
from routes.files import files_bp
from routes.ai import ai_bp
from routes.index import index_bp
from database import init_db
import os
import humanize
import json

app = Flask(__name__, 
    template_folder=os.path.abspath('templates'),
    static_folder=os.path.abspath('static'))
app.secret_key = 'your_secret_key_here'

# 注册 Jinja2 过滤器
app.jinja_env.filters['filesizeformat'] = humanize.naturalsize

# 注册蓝图
app.register_blueprint(index_bp)
app.register_blueprint(storage_bp, url_prefix='/storage')
app.register_blueprint(files_bp, url_prefix='/files')
app.register_blueprint(ai_bp, url_prefix='/ai')

# 添加from_json过滤器
@app.template_filter('from_json')
def from_json_filter(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return value

# 初始化数据库
init_db()

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True) 