"""
启动脚本
"""
import uvicorn
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from module.config import Config

# 加载配置
config = Config()

# 获取服务器配置
host = config.get("server.host", "0.0.0.0")
port = config.get("server.port", 5000)
reload = config.get("server.reload", False)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=config.get("logging.level", "INFO").lower()
    )
