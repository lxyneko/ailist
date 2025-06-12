# AiList

AiList 是一个现代化的文件管理系统，支持多种存储后端，提供优雅的用户界面和强大的文件管理功能。

## 特性

- 支持多种存储后端
- 文件预览功能
- 文件管理（上传、下载、删除等）
- WebDAV 支持
- 用户认证系统
- 响应式设计
- 暗色模式支持

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- Alembic
- Python 3.8+

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

2. 安装后端依赖
```bash
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

4. 启动开发服务器
```bash
# 后端
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 许可证

MIT License 