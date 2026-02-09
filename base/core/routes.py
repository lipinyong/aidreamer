"""
核心路由设置 - 修复版本
"""
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import aiofiles
import json

from module.config import Config
from module.webhandle import WebHandle
from module.markdown import MarkdownRenderer
from module.logger import setup_logger


security = HTTPBearer(auto_error=False)


async def verify_token(
    request: Request,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = None,
    config: Config = None
) -> bool:
    """
    验证 Token
    
    Token 可以从以下位置获取:
    1. Authorization Header: Bearer <token>
    2. 查询参数: ?token=<token>
    """
    # 从 Header 获取（authorization 可能是 Header 对象，需要转换为字符串）
    auth_header = None
    if authorization:
        if isinstance(authorization, str):
            auth_header = authorization
        else:
            # 如果是 Header 对象，尝试获取其值
            auth_header = str(authorization) if authorization else None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    # 从查询参数获取
    if not token:
        token = request.query_params.get("token")
    
    if not token:
        return False
    
    # 检查系统级 Token
    system_tokens = config.get("security.system_tokens", [])
    for sys_token in system_tokens:
        if sys_token.get("token") == token:
            return True
    
    # TODO: 检查登录 Token（需要实现 Session 管理）
    # 这里可以对接 Sessions 服务
    
    return False


def setup_routes(
    app: FastAPI,
    config: Config,
    webhandle: WebHandle,
    markdown_renderer: MarkdownRenderer,
    logger
):
    """设置核心路由"""
    
    base_dir = Path(__file__).parent.parent
    web_dir = base_dir / "web"
    
    # 根路径路由（必须在 /{path:path} 之前注册）
    @app.get("/")
    async def root_path_handler(request: Request):
        """根路径处理器 - 优先匹配 /"""
        logger.info("根路径处理器被调用")
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
    
    def _resolve_raw_path(path: str) -> Path:
        """解析 /raw/ 路径，返回安全的文件路径"""
        if path.startswith("etc/"):
            file_path = base_dir / path
            etc_dir = base_dir / "etc"
            try:
                file_path.resolve().relative_to(etc_dir.resolve())
            except ValueError:
                raise HTTPException(status_code=403, detail="访问被拒绝")
        else:
            file_path = web_dir / path
            try:
                file_path.resolve().relative_to(web_dir.resolve())
            except ValueError:
                raise HTTPException(status_code=403, detail="访问被拒绝")
        return file_path

    @app.get("/raw/{path:path}")
    async def read_raw_file(path: str):
        """
        读取文件原始内容
        py 文件不执行，md 文件不渲染，直接输出原内容
        不支持二进制文件
        支持访问 web/ 和 etc/ 目录下的文件
        """
        file_path = _resolve_raw_path(path)
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip']:
            raise HTTPException(status_code=400, detail="不支持二进制文件")
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return Response(content=content, media_type="text/plain")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")

    @app.put("/raw/{path:path}")
    async def write_raw_file(path: str, request: Request):
        """
        写入文件原始内容
        支持写入 web/ 和 etc/ 目录下的文件
        """
        file_path = _resolve_raw_path(path)
        
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip']:
            raise HTTPException(status_code=400, detail="不支持二进制文件")
        
        try:
            body = await request.body()
            content = body.decode('utf-8')
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            if path == "etc/config.yaml":
                config.reload()
                logger.info("配置文件已更新并重新加载")
            
            return JSONResponse(content={"success": True, "message": "文件保存成功"})
        except Exception as e:
            logger.error(f"写入文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"写入文件失败: {str(e)}")
    
    @app.get("/tree/{path:path}")
    @app.post("/tree/{path:path}")
    @app.put("/tree/{path:path}")
    @app.delete("/tree/{path:path}")
    async def manage_tree(path: str, request: Request):
        """
        目录管理接口
        GET: 列出目录和文件
        POST: 创建文件或目录
        PUT: 重命名文件或目录
        DELETE: 删除文件或目录
        """
        # TODO: 添加权限检查
        target_path = web_dir / path
        
        # 安全检查
        try:
            target_path.resolve().relative_to(web_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="访问被拒绝")
        
        if request.method == "GET":
            # 列出目录内容
            if not target_path.exists():
                raise HTTPException(status_code=404, detail="路径不存在")
            
            items = []
            if target_path.is_dir():
                for item in target_path.iterdir():
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0,
                        "modified": item.stat().st_mtime
                    })
            
            return JSONResponse(content={"path": path, "items": items})
        
        elif request.method == "POST":
            # 创建文件或目录
            data = await request.json()
            item_type = data.get("type", "file")  # file or directory
            content = data.get("content", "")
            
            if item_type == "directory":
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(target_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
            
            return JSONResponse(content={"message": "创建成功", "path": path})
        
        elif request.method == "PUT":
            # 重命名
            data = await request.json()
            new_name = data.get("name")
            if not new_name:
                raise HTTPException(status_code=400, detail="缺少新名称")
            
            new_path = target_path.parent / new_name
            target_path.rename(new_path)
            return JSONResponse(content={"message": "重命名成功"})
        
        elif request.method == "DELETE":
            # 删除
            if target_path.exists():
                if target_path.is_dir():
                    import shutil
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
                return JSONResponse(content={"message": "删除成功"})
            else:
                raise HTTPException(status_code=404, detail="路径不存在")
       
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def api_handler(path: str, request: Request):
        """
        API 执行接口
        查找 web/{path}.py 文件，存在则加载运行
        """
        # 检查是否启用 API 认证
        api_auth_enabled = config.get("security.api_auth_enabled", True)
        
        if api_auth_enabled:
            # Token 验证（从 request 中获取 authorization header）
            auth_header = request.headers.get("authorization")
            is_authenticated = False
            if auth_header and isinstance(auth_header, str) and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                # 检查系统级 Token
                system_tokens = config.get("security.system_tokens", [])
                for sys_token in system_tokens:
                    if sys_token.get("token") == token:
                        is_authenticated = True
                        break
            
            # 也可以从查询参数获取 token
            if not is_authenticated:
                token = request.query_params.get("token")
                if token:
                    system_tokens = config.get("security.system_tokens", [])
                    for sys_token in system_tokens:
                        if sys_token.get("token") == token:
                            is_authenticated = True
                            break
            
            if not is_authenticated:
                raise HTTPException(status_code=401, detail="需要认证")
        
        # 移除扩展名（如果有）
        if path.endswith('.py'):
            path = path[:-3]
        
        # 使用 webhandle 处理请求
        return await webhandle.handle_request(request, path)

    @app.get("/openapi.json")
    async def openapi_schema():
        """OpenAPI 文档（自动生成）"""
        # TODO: 自动扫描 web/ 目录下的 Python 文件并生成 OpenAPI 文档
        return JSONResponse(content=app.openapi())
        
    @app.get("/{path:path}")
    async def web_handler(path: str, request: Request):
        """
        Web 访问接口
        如果 path 是目录，查找默认文件
        如果 path 是 Python 文件，执行并返回结果
        如果 path 是 Markdown 文件，渲染为 HTML
        """
        # 处理根路径：直接查找并处理默认文件
        path = path.strip('/')
        
        # 如果是根路径（空路径），直接查找并处理默认文件
        if not path:
            logger.info("web_handler 处理根路径请求")
            logger.info(f"处理根路径请求，从配置读取默认文件列表")
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
                        else:
                            logger.warning(f"Markdown 渲染失败: {default_file}")
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
        
        # 构建目标路径
        target_path = web_dir / path
        
        # 安全检查：确保路径在 web_dir 内
        try:
            resolved_target = target_path.resolve()
            resolved_web = web_dir.resolve()
            relative_path = resolved_target.relative_to(resolved_web)
            # 额外检查：确保没有路径遍历攻击
            if '..' in str(relative_path):
                raise HTTPException(status_code=403, detail="访问被拒绝")
        except ValueError:
            logger.error(f"路径安全检查失败: path={path}")
            raise HTTPException(status_code=403, detail="访问被拒绝")
        
        # 如果是目录，查找默认文件
        if target_path.exists() and target_path.is_dir():
            default_files = config.get("default_files", ["index.html", "index.md", "index.py"])
            for default_file in default_files:
                default_path = target_path / default_file
                if default_path.exists():
                    # 构建新的路径
                    new_path = f"{path.rstrip('/')}/{default_file}".lstrip('/')
                    # 递归处理默认文件
                    return await web_handler(new_path, request)
            raise HTTPException(status_code=404, detail="目录下没有默认文件")
        
        # 如果是 Python 文件，执行
        if target_path.suffix == '.py':
            result = await webhandle.handle_request(request, str(target_path.relative_to(web_dir))[:-3])
            return result
        
        # 如果是 Markdown 文件，渲染
        elif target_path.suffix in ['.md', '.markdown']:
            html = markdown_renderer.render_file(target_path)
            if html:
                return HTMLResponse(content=html)
            else:
                raise HTTPException(status_code=500, detail="渲染失败")
        
        # 如果是 HTML 文件，直接返回
        elif target_path.suffix == '.html':
            if target_path.exists():
                async with aiofiles.open(target_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                return HTMLResponse(content=content)
            else:
                raise HTTPException(status_code=404, detail="文件不存在")
        
        # 其他文件，尝试作为静态文件返回
        elif target_path.exists() and target_path.is_file():
            return FileResponse(target_path)
        
        else:
            raise HTTPException(status_code=404, detail="文件不存在")
    

