"""
Web 服务处理模块
用于处理 web/ 目录下的 Python 文件
"""
import importlib.util
import sys
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import traceback


class WebHandle:
    """Web 处理类，用于注册和管理 web/ 目录下的路由"""
    
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.base_dir = Path(__file__).parent.parent
        self.web_dir = self.base_dir / "web"
        self.routes: Dict[str, Callable] = {}
        self._loaded_modules: Dict[str, Any] = {}
    
    def route(self, path: str, methods: list = None):
        """
        路由装饰器
        
        用法:
        @webhandle.route('/example/hello')
        def hello(request):
            return {'message': 'hello world'}
        """
        if methods is None:
            methods = ["GET", "POST"]
        
        def decorator(func: Callable):
            # 注册路由到 FastAPI
            async def handler(request: Request):
                try:
                    result = func(request)
                    if isinstance(result, Response):
                        return result
                    elif isinstance(result, dict) or isinstance(result, list):
                        return JSONResponse(content=result)
                    else:
                        return JSONResponse(content={"result": str(result)})
                except Exception as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": str(e), "traceback": traceback.format_exc()}
                    )
            
            # 为每个方法注册路由
            for method in methods:
                self.app.add_api_route(path, handler, methods=[method])
            
            self.routes[path] = func
            return func
        
        return decorator
    
    def load_module(self, file_path: Path) -> Optional[Any]:
        """
        动态加载 Python 模块
        
        Args:
            file_path: Python 文件路径（相对于 web/ 目录）
        
        Returns:
            加载的模块对象，失败返回 None
        """
        # 转换为绝对路径
        if not file_path.is_absolute():
            file_path = self.web_dir / file_path
        
        if not file_path.exists() or not file_path.suffix == '.py':
            return None
        
        # 生成模块名
        module_name = f"web_{file_path.stem}_{id(file_path)}"
        
        # 如果已加载，先移除
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        try:
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # 设置模块的 webhandle 引用
            module.webhandle = self
            
            # 执行模块
            spec.loader.exec_module(module)
            
            self._loaded_modules[str(file_path)] = module
            return module
        
        except Exception as e:
            print(f"加载模块失败 {file_path}: {e}")
            traceback.print_exc()
            return None
    
    async def handle_request(self, request: Request, path: str) -> Response:
        """
        处理请求
        
        Args:
            request: FastAPI 请求对象
            path: 请求路径（相对于 web/ 目录，不含扩展名）
        
        Returns:
            FastAPI 响应对象
        """
        # 先尝试精确匹配
        file_path = self.web_dir / f"{path}.py"
        sub_path = ''
        
        # 如果精确匹配不存在，尝试向上查找父路径
        if not file_path.exists():
            parts = path.split('/')
            for i in range(len(parts) - 1, 0, -1):
                parent_path = '/'.join(parts[:i])
                parent_file = self.web_dir / f"{parent_path}.py"
                if parent_file.exists():
                    file_path = parent_file
                    sub_path = '/'.join(parts[i:])
                    break
        
        # 将 sub_path 存入 request.state
        request.state.sub_path = sub_path
        
        # 加载模块
        module = self.load_module(file_path)
        
        if module is None:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 查找处理函数（通常命名为 handle 或 main）
        handler = None
        for attr_name in ['handle', 'main', 'handler']:
            if hasattr(module, attr_name):
                handler = getattr(module, attr_name)
                break
        
        # 如果没有找到处理函数，尝试执行模块的默认行为
        if handler is None:
            # 检查是否有默认导出
            if hasattr(module, '__all__'):
                exports = getattr(module, '__all__')
                if exports:
                    handler = getattr(module, exports[0])
        
        if handler is None:
            raise HTTPException(status_code=500, detail="未找到处理函数")
        
        try:
            # 调用处理函数（支持同步和异步）
            import asyncio
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request)
            else:
                result = handler(request)
            
            # 处理返回值
            if isinstance(result, Response):
                return result
            elif isinstance(result, dict) or isinstance(result, list):
                return JSONResponse(content=result)
            elif isinstance(result, str):
                return Response(content=result, media_type="text/plain")
            else:
                return JSONResponse(content={"result": str(result)})
        
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
    
    def reload_module(self, file_path: Path):
        """重新加载模块"""
        if str(file_path) in self._loaded_modules:
            del self._loaded_modules[str(file_path)]
        return self.load_module(file_path)
