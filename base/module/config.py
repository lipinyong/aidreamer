"""
配置管理模块
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 加载环境变量
load_dotenv()


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""
    
    def __init__(self, config_instance):
        self.config = config_instance
    
    def on_modified(self, event):
        if event.src_path.endswith('config.yaml'):
            self.config.reload()


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        self.config_path = Path(config_path) if config_path else self.base_dir / "etc" / "config.yaml"
        self._config: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self.observer = None
        
        # 加载配置
        self.load()
        
        # 启动文件监控
        self._start_watcher()
    
    def _start_watcher(self):
        """启动配置文件监控"""
        try:
            self.observer = Observer()
            event_handler = ConfigFileHandler(self)
            self.observer.schedule(event_handler, str(self.config_path.parent), recursive=False)
            self.observer.start()
        except Exception as e:
            print(f"配置文件监控启动失败: {e}")
    
    def load(self):
        """加载配置文件"""
        with self._lock:
            # 加载 YAML 配置
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = {}
            
            # 处理环境变量替换
            self._resolve_env_vars(self._config)
    
    def _resolve_env_vars(self, obj: Any):
        """递归解析环境变量"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._resolve_env_vars(value)
        elif isinstance(obj, list):
            return [self._resolve_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            # 提取环境变量名
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def reload(self):
        """重新加载配置"""
        self.load()
        # 触发配置变更事件（如果需要）
        # 这里可以添加配置变更回调
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        例如: config.get("server.port") 等同于 config._config["server"]["port"]
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def save(self):
        """保存配置到文件"""
        with self._lock:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def update_oauth2_config(self, oauth2_config: Dict[str, Any]):
        """更新 OAuth2 配置"""
        with self._lock:
            # 如果 oauth2 配置不存在，创建它
            if 'oauth2' not in self._config:
                self._config['oauth2'] = {}
            
            # 更新 oauth2 配置
            self._config['oauth2'].update(oauth2_config)
            
            # 保存到文件
            self.save()
    
    def __del__(self):
        """清理资源"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
