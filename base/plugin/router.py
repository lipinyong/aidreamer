"""
插件管理器
"""
import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Callable, Any
from fastapi import Request, Response
import logging


class Plugin:
    """插件基类"""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
        self.enabled = True
    
    async def pre_process(self, request: Request) -> Request:
        """预处理（路由匹配前）"""
        return request
    
    async def post_process(self, request: Request, response: Response) -> Response:
        """后处理（路由处理完成后）"""
        return response


class PluginManager:
    """插件管理器"""
    
    def __init__(self, config):
        self.config = config
        self.base_dir = Path(__file__).parent.parent
        self.plugin_dir = self.base_dir / "plugin"
        self.plugins: List[Plugin] = []
        self.logger = logging.getLogger("baseplatform.plugin")
        self._loaded_modules: Dict[str, Any] = {}
    
    async def load_plugins(self):
        """加载所有插件"""
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # 扫描插件目录
        for file_path in self.plugin_dir.rglob("*.py"):
            if file_path.name == "__init__.py":
                continue
            
            try:
                plugin = self._load_plugin(file_path)
                if plugin:
                    self.plugins.append(plugin)
                    self.logger.info(f"加载插件: {plugin.name}")
            except Exception as e:
                self.logger.error(f"加载插件失败 {file_path}: {e}")
        
        # 按优先级排序
        self.plugins.sort(key=lambda p: p.priority)
    
    def _load_plugin(self, file_path: Path) -> Plugin:
        """加载单个插件"""
        module_name = f"plugin_{file_path.stem}_{id(file_path)}"
        
        # 如果已加载，先移除
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # 加载模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # 查找插件类
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Plugin) and 
                attr != Plugin):
                plugin_class = attr
                break
        
        if plugin_class is None:
            # 如果没有找到插件类，创建一个默认的
            plugin_instance = Plugin(file_path.stem)
        else:
            plugin_instance = plugin_class()
        
        self._loaded_modules[str(file_path)] = module
        return plugin_instance
    
    async def apply_pre_process(self, request: Request) -> Request:
        """应用所有插件的预处理"""
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    request = await plugin.pre_process(request)
                except Exception as e:
                    self.logger.error(f"插件预处理失败 {plugin.name}: {e}")
        return request
    
    async def apply_post_process(self, request: Request, response: Response) -> Response:
        """应用所有插件的后处理"""
        for plugin in reversed(self.plugins):  # 反向处理
            if plugin.enabled:
                try:
                    response = await plugin.post_process(request, response)
                except Exception as e:
                    self.logger.error(f"插件后处理失败 {plugin.name}: {e}")
        return response
    
    def reload_plugin(self, file_path: Path):
        """重新加载插件"""
        # 移除旧插件
        plugin_name = file_path.stem
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
        
        # 重新加载
        plugin = self._load_plugin(file_path)
        if plugin:
            self.plugins.append(plugin)
            self.plugins.sort(key=lambda p: p.priority)
