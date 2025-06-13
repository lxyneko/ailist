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
- FastAPI 0.68.1
- SQLAlchemy 2.0+
- Alembic 1.12.1
- Python 3.8+
- OpenAI API 集成
- 文件处理库（python-docx, openpyxl, python-pptx, Pillow）

### 前端
- SCSS
- TypeScript
- React
- TailwindCSS

## 开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ailist.git
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

4. 安装前端依赖
```bash
cd frontend
npm install
```

5. 配置环境变量
创建 `.env` 文件并设置必要的环境变量：
```env
DATABASE_URL=sqlite:///./ailist.db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

6. 启动开发服务器
```bash
# 后端
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 项目结构

```
ailist/
├── app/            # 主应用目录
├── models/         # 数据模型
├── routes/         # API 路由
├── static/         # 静态文件
├── storage/        # 文件存储
├── templates/      # 模板文件
├── frontend/       # 前端代码
├── requirements.txt # Python 依赖
└── README.md       # 项目文档
```

## 许可证

MIT License 