"""
文件监控模块
用于监控目录变化并自动重新加载
"""
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
import logging


class FileWatcherHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, watcher):
        self.watcher = watcher
        self.logger = logging.getLogger("baseplatform.file_watcher")
    
    def on_modified(self, event):
        if not event.is_directory:
            self.watcher.on_file_changed(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self.watcher.on_file_created(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.watcher.on_file_deleted(event.src_path)


class FileWatcher:
    """文件监控器"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.base_dir = Path(__file__).parent.parent
        self.observer = None
        self.watched_dirs = []
        self.callbacks: dict = {
            'module': [],
            'plugin': [],
            'service': [],
            'config': [],
        }
    
    def add_callback(self, category: str, callback: Callable):
        """添加文件变更回调"""
        if category in self.callbacks:
            self.callbacks[category].append(callback)
    
    def start(self):
        """启动文件监控"""
        try:
            self.observer = Observer()
            handler = FileWatcherHandler(self)
            
            # 监控 module 目录
            module_dir = self.base_dir / "module"
            if module_dir.exists():
                self.observer.schedule(handler, str(module_dir), recursive=True)
                self.watched_dirs.append(module_dir)
                self.logger.info(f"监控目录: {module_dir}")
            
            # 监控 plugin 目录
            plugin_dir = self.base_dir / "plugin"
            if plugin_dir.exists():
                self.observer.schedule(handler, str(plugin_dir), recursive=True)
                self.watched_dirs.append(plugin_dir)
                self.logger.info(f"监控目录: {plugin_dir}")
            
            # 监控 service 目录
            service_dir = self.base_dir / "service"
            if service_dir.exists():
                self.observer.schedule(handler, str(service_dir), recursive=True)
                self.watched_dirs.append(service_dir)
                self.logger.info(f"监控目录: {service_dir}")
            
            # 监控 etc 目录（配置文件）
            etc_dir = self.base_dir / "etc"
            if etc_dir.exists():
                self.observer.schedule(handler, str(etc_dir), recursive=True)
                self.watched_dirs.append(etc_dir)
                self.logger.info(f"监控目录: {etc_dir}")
            
            self.observer.start()
            self.logger.info("文件监控已启动")
        
        except Exception as e:
            self.logger.error(f"启动文件监控失败: {e}")
    
    def stop(self):
        """停止文件监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("文件监控已停止")
    
    def on_file_changed(self, file_path: str):
        """文件变更处理"""
        path = Path(file_path)
        relative_path = path.relative_to(self.base_dir)
        
        # 判断文件类型并触发相应回调
        if relative_path.parts[0] == "module":
            self._trigger_callbacks('module', path)
        elif relative_path.parts[0] == "plugin":
            self._trigger_callbacks('plugin', path)
        elif relative_path.parts[0] == "service":
            self._trigger_callbacks('service', path)
        elif relative_path.parts[0] == "etc" and path.name == "config.yaml":
            self._trigger_callbacks('config', path)
    
    def on_file_created(self, file_path: str):
        """文件创建处理"""
        self.on_file_changed(file_path)
    
    def on_file_deleted(self, file_path: str):
        """文件删除处理"""
        # 可以在这里处理文件删除逻辑
        pass
    
    def _trigger_callbacks(self, category: str, file_path: Path):
        """触发回调函数"""
        for callback in self.callbacks.get(category, []):
            try:
                callback(file_path)
            except Exception as e:
                self.logger.error(f"执行回调失败 {category}: {e}")
