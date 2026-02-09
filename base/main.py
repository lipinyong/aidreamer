"""
Base Platform 主程序入口
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import aiofiles
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from module.config import Config
from module.logger import setup_logger
from module.webhandle import WebHandle
from module.markdown import MarkdownRenderer
from plugin.router import PluginManager
from service.jsonserv.router import setup_jsonserv
from service.datasource import DataSourceManager
from service.cron import CronManager
from core.file_watcher import FileWatcher
from core.routes import setup_routes

# 初始化配置
config = Config()
logger = setup_logger(config)

# 创建 FastAPI 应用
app = FastAPI(
    title=config.get("app.name", "FastAPI Base Platform"),
    version=config.get("app.version", "1.0.0"),
    docs_url=None,  # 禁用默认的 /docs
    redoc_url=None,  # 禁用默认的 /redoc
)

# 将 config 挂载到 app.state，供 web 模块使用
app.state.config = config

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
webhandle = WebHandle(app, config)
markdown_renderer = MarkdownRenderer()
plugin_manager = PluginManager(config)
jsonserv_manager = None
datasource_manager = DataSourceManager(config)
cron_manager = CronManager(config)
file_watcher = FileWatcher(config, logger)

# 健康检查（必须在 setup_routes 之前注册，避免被 /{path:path} 匹配）
@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "ok", "service": "baseplatform"}

# 根路径路由（必须在 setup_routes 之前注册，确保优先匹配）
@app.get("/")
async def root_handler(request: Request):
    """根路径处理器 - 从配置读取默认文件并依次查找"""
    logger.info("根路径处理器被调用")
    from pathlib import Path
    web_dir = Path(__file__).parent / "web"
    
    # 从配置读取默认文件列表
    default_files = config.get("default_files", ["index.html", "index.md", "index.py"])
    logger.info(f"默认文件列表: {default_files}")
    
    # 依次查找默认文件
    for default_file in default_files:
        default_path = web_dir / default_file
        logger.info(f"检查默认文件: {default_path}, 存在: {default_path.exists()}")
        
        if default_path.exists():
            logger.info(f"找到默认文件: {default_file}, 类型: {default_path.suffix}")
            
            # 根据文件类型处理
            if default_path.suffix == '.md':
                html = markdown_renderer.render_file(default_path)
                if html:
                    logger.info(f"成功渲染 Markdown 文件: {default_file}")
                    return HTMLResponse(content=html)
            elif default_path.suffix == '.html':
                async with aiofiles.open(default_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                logger.info(f"成功读取 HTML 文件: {default_file}")
                return HTMLResponse(content=content)
            elif default_path.suffix == '.py':
                result = await webhandle.handle_request(request, str(default_path.relative_to(web_dir))[:-3])
                logger.info(f"成功执行 Python 文件: {default_file}")
                return result
    
    # 没有找到任何默认文件
    logger.error("未找到任何默认文件")
    raise HTTPException(status_code=404, detail="目录下没有默认文件")

# 设置路由
setup_routes(app, config, webhandle, markdown_renderer, logger)

# 设置 jsonserv
if config.get("jsonserv.enabled", True):
    jsonserv_manager = setup_jsonserv(app, config)

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    logger.info("Base Platform 启动中...")
    
    # 加载插件
    await plugin_manager.load_plugins()
    
    # 加载数据源
    await datasource_manager.load_datasources()
    
    # 启动计划任务
    await cron_manager.start()
    
    # 启动文件监控
    file_watcher.start()
    
    logger.info("Base Platform 启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    logger.info("Base Platform 关闭中...")
    
    # 停止文件监控
    file_watcher.stop()
    
    # 停止计划任务
    await cron_manager.stop()
    
    logger.info("Base Platform 已关闭")

if __name__ == "__main__":
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 5000)
    reload = config.get("server.reload", False)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=config.get("logging.level", "INFO").lower()
    )
