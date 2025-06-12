from flask import Flask, send_from_directory
from routes.storage import storage_bp
from routes.files import files_bp
from database import init_db

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(storage_bp)
app.register_blueprint(files_bp)

# 初始化数据库
init_db()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True) 