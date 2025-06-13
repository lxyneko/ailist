# AiList

AiList 是一个现代化的文件管理系统，支持多种存储后端，提供优雅的用户界面和强大的文件管理功能。

## 特性

- 支持多种存储后端（本地存储、S3、WebDAV等）
- 智能文件预览功能（支持图片、文档、表格等）
- 完整的文件管理功能（上传、下载、删除、重命名等）
- WebDAV 协议支持
- 安全的用户认证系统
- 响应式设计，支持移动端
- 暗色模式支持
- AI 辅助功能

## 技术栈

### 后端
- Flask 2.0.1
- FastAPI 0.68.1
- SQLAlchemy 2.0+
- Alembic 1.12.1
- Python 3.8+
- OpenAI API 集成
- 文件处理库（python-docx, openpyxl, python-pptx, Pillow）
- WebDAV 客户端支持
- AWS S3 集成

### 前端
- SCSS
- TypeScript
- React
- TailwindCSS

## 开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/lxyneko/ailist.git
cd ailist
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装后端依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
创建 `.env` 文件并设置必要的环境变量：
```env
DATABASE_URL=sqlite:///./ailist.db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
```

5. 启动开发服务器
```bash
# 使用 Flask
python app.py

# 或使用 FastAPI
uvicorn app.main:app --reload
```

## 项目结构

```
ailist/
├── app/            # FastAPI 应用目录
├── models/         # 数据模型
├── routes/         # API 路由
├── services/       # 业务逻辑服务
├── static/         # 静态文件
├── storage/        # 文件存储
├── templates/      # 模板文件
├── venv/           # Python 虚拟环境
├── .venv/          # 备用虚拟环境
├── app.py          # Flask 应用入口
├── database.py     # 数据库配置
├── requirements.txt # Python 依赖
├── test_api.py     # API 测试
└── README.md       # 项目文档
```

## 测试

项目包含完整的测试套件，可以通过以下命令运行测试：

```bash
python test_api.py
```

## 许可证

MIT License 