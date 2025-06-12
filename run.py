import uvicorn
from app.database import init_db
import os

# 确保 static 目录存在
os.makedirs("static", exist_ok=True)

# 初始化数据库
init_db()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["static", "app"]
    )