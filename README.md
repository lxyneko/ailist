# AiList

一个现代化的文件管理系统，集成了AI智能分析功能。

## 免责声明

本项目仅供个人学习使用，不保证功能实现。使用本项目产生的任何问题，作者不承担任何责任。

## 功能特点

- 文件管理：上传、下载、删除文件
- 存储管理：支持本地存储和S3存储
- AI分析：文件内容分析、标签生成、情感分析
- 智能搜索：语义搜索、关键词搜索、内容搜索
- 多语言支持：支持中文和英文内容分析

## 技术栈

- 后端：Python + Flask
- 数据库：SQLite
- 前端：HTML + CSS + JavaScript + Bootstrap
- AI：DeepSeek API

## 安装

1. 克隆项目
```bash
git clone https://github.com/yourusername/ailist.git
cd ailist
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 初始化数据库
```bash
python init_db.py
```

4. 运行应用
```bash
python app.py
```

## 配置

1. 配置存储池
   - 本地存储：设置存储路径
   - S3存储：配置Access Key、Secret Key、Bucket和Region

2. 配置AI
   - 设置DeepSeek API密钥
   - 调整温度参数

## 使用说明

1. 文件管理
   - 上传文件：支持拖拽上传和批量上传
   - 下载文件：点击下载按钮
   - 删除文件：点击删除按钮

2. 存储管理
   - 创建存储池：设置名称和类型
   - 激活存储池：点击激活按钮
   - 编辑存储池：修改配置信息
   - 删除存储池：点击删除按钮

3. AI分析
   - 配置API：设置API密钥和参数
   - 分析文件：点击AI分析按钮
   - 查看结果：显示摘要、标签和情感分析

4. 智能搜索
   - 语义搜索：基于文件内容的语义理解
   - 关键词搜索：基于标签和文件名
   - 内容搜索：基于文件内容

## 注意事项

1. 本项目仅供学习使用，不建议用于生产环境
2. 使用前请确保已正确配置存储池和AI API
3. 定期备份重要数据
4. 注意API使用限制和费用

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT License 