"""
数据源服务
"""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging


class DataSource:
    """数据源类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"baseplatform.datasource.{name}")
    
    def query(self, sql: str) -> Any:
        """
        执行查询
        
        这是一个基础实现，具体的数据源需要继承此类并实现具体逻辑
        """
        raise NotImplementedError("子类需要实现 query 方法")
    
    def execute(self, sql: str) -> Any:
        """
        执行 SQL（非查询）
        """
        raise NotImplementedError("子类需要实现 execute 方法")


class FileDataSource(DataSource):
    """文件数据源"""
    
    def query(self, sql: str) -> Any:
        """文件数据源暂不支持 SQL 查询"""
        raise NotImplementedError("文件数据源不支持 SQL 查询")
    
    def execute(self, sql: str) -> Any:
        """文件数据源暂不支持 SQL 执行"""
        raise NotImplementedError("文件数据源不支持 SQL 执行")


class SQLiteDataSource(DataSource):
    """SQLite 数据源"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.db_path = Path(config.get("path", ""))
        # TODO: 实现 SQLite 连接
    
    def query(self, sql: str) -> Any:
        """执行查询"""
        # TODO: 实现 SQLite 查询
        raise NotImplementedError("SQLite 数据源待实现")
    
    def execute(self, sql: str) -> Any:
        """执行 SQL"""
        # TODO: 实现 SQLite 执行
        raise NotImplementedError("SQLite 数据源待实现")


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, config):
        self.config = config
        self.base_dir = Path(__file__).parent.parent.parent
        self.datasource_dir = self.base_dir / "service" / "datasource"
        self.datasources: Dict[str, DataSource] = {}
        self.logger = logging.getLogger("baseplatform.datasource")
    
    async def load_datasources(self):
        """加载所有数据源"""
        if not self.datasource_dir.exists():
            self.datasource_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # 扫描数据源目录
        for ds_dir in self.datasource_dir.iterdir():
            if not ds_dir.is_dir():
                continue
            
            config_file = ds_dir / "config.yaml"
            if not config_file.exists():
                continue
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    ds_config = yaml.safe_load(f)
                
                # 创建数据源实例
                ds_type = ds_config.get("type", "file")
                if ds_type == "file":
                    datasource = FileDataSource(ds_dir.name, ds_config)
                elif ds_type == "sqlite":
                    datasource = SQLiteDataSource(ds_dir.name, ds_config)
                else:
                    self.logger.warning(f"未知的数据源类型: {ds_type}")
                    continue
                
                self.datasources[ds_dir.name] = datasource
                self.logger.info(f"加载数据源: {ds_dir.name}")
            
            except Exception as e:
                self.logger.error(f"加载数据源失败 {ds_dir.name}: {e}")
    
    def get(self, name: str) -> Optional[DataSource]:
        """获取数据源"""
        return self.datasources.get(name)


# 全局数据源管理器实例（在 main.py 中初始化）
_manager: Optional[DataSourceManager] = None


def get_datasource(name: str) -> Optional[DataSource]:
    """获取数据源的便捷函数"""
    global _manager
    if _manager:
        return _manager.get(name)
    return None
