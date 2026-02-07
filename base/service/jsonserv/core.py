"""
jsonserv 核心逻辑
JSON 读写、查询过滤算法
"""
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from filelock import FileLock
import logging


class JSONDataStore:
    """JSON 数据存储"""
    
    def __init__(self, file_path: Path, primary_key: str = "id"):
        self.file_path = file_path
        self.primary_key = primary_key
        self.lock = FileLock(str(file_path) + ".lock")
        self.logger = logging.getLogger("baseplatform.jsonserv")
        self._cache: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """加载 JSON 数据"""
        if self._cache is not None:
            return self._cache
        
        if not self.file_path.exists():
            # 创建空文件
            data = {"data": [], "primary_key": self.primary_key}
            self.save(data)
            return data
        
        try:
            with self.lock:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # 处理数据格式
            if isinstance(data, list):
                # 场景 A: 列表模式
                data = {"data": data, "primary_key": self.primary_key}
            elif isinstance(data, dict):
                # 场景 B: 对象模式
                if "data" not in data:
                    # 如果根对象包含多个键，转换为标准格式
                    if "primary_key" not in data:
                        data = {"data": list(data.values())[0] if data else [], "primary_key": self.primary_key}
            
            self._cache = data
            return data
        
        except Exception as e:
            self.logger.error(f"加载 JSON 文件失败 {self.file_path}: {e}")
            return {"data": [], "primary_key": self.primary_key}
    
    def save(self, data: Dict[str, Any]):
        """保存 JSON 数据"""
        try:
            with self.lock:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            self._cache = data
        except Exception as e:
            self.logger.error(f"保存 JSON 文件失败 {self.file_path}: {e}")
            raise
    
    def get_items(self) -> List[Dict[str, Any]]:
        """获取所有数据项"""
        data = self.load()
        return data.get("data", [])
    
    def get_item(self, item_id: Any) -> Optional[Dict[str, Any]]:
        """根据 ID 获取数据项"""
        items = self.get_items()
        primary_key = self.load().get("primary_key", self.primary_key)
        
        for item in items:
            if item.get(primary_key) == item_id:
                return item
        return None
    
    def add_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """添加数据项"""
        data = self.load()
        items = data.get("data", [])
        primary_key = data.get("primary_key", self.primary_key)
        
        # 如果没有 ID，自动生成
        if primary_key not in item:
            if primary_key == "id":
                # 生成数字 ID
                existing_ids = [i.get(primary_key, 0) for i in items if isinstance(i.get(primary_key), int)]
                item[primary_key] = max(existing_ids, default=0) + 1
            else:
                # 生成 UUID
                item[primary_key] = str(uuid.uuid4())
        
        items.append(item)
        data["data"] = items
        self.save(data)
        return item
    
    def update_item(self, item_id: Any, item: Dict[str, Any], partial: bool = False) -> Optional[Dict[str, Any]]:
        """更新数据项"""
        data = self.load()
        items = data.get("data", [])
        primary_key = data.get("primary_key", self.primary_key)
        
        for i, existing_item in enumerate(items):
            if existing_item.get(primary_key) == item_id:
                if partial:
                    # 部分更新
                    items[i] = {**existing_item, **item}
                else:
                    # 全量更新
                    item[primary_key] = item_id
                    items[i] = item
                data["data"] = items
                self.save(data)
                return items[i]
        return None
    
    def delete_item(self, item_id: Any) -> bool:
        """删除数据项"""
        data = self.load()
        items = data.get("data", [])
        primary_key = data.get("primary_key", self.primary_key)
        
        for i, item in enumerate(items):
            if item.get(primary_key) == item_id:
                items.pop(i)
                data["data"] = items
                self.save(data)
                return True
        return False
    
    def query(self, filters: Dict[str, Any] = None, sort: str = None, order: str = "asc", 
              page: int = None, limit: int = None, start: int = None, end: int = None,
              search: str = None) -> List[Dict[str, Any]]:
        """
        查询数据
        
        Args:
            filters: 字段过滤条件
            sort: 排序字段
            order: 排序方向 (asc/desc)
            page: 页码（从1开始）
            limit: 每页数量
            start: 起始索引
            end: 结束索引
            search: 全文搜索关键词
        """
        items = self.get_items()
        
        # 字段过滤
        if filters:
            filtered_items = []
            for item in items:
                match = True
                for key, value in filters.items():
                    if key.startswith("_"):  # 跳过特殊参数
                        continue
                    item_value = item.get(key)
                    if isinstance(item_value, list):
                        # 列表包含检查
                        if value not in item_value:
                            match = False
                            break
                    elif item_value != value:
                        match = False
                        break
                if match:
                    filtered_items.append(item)
            items = filtered_items
        
        # 全文搜索
        if search:
            search_lower = search.lower()
            items = [
                item for item in items
                if any(search_lower in str(v).lower() for v in item.values())
            ]
        
        # 排序
        if sort:
            reverse = (order.lower() == "desc")
            try:
                items.sort(key=lambda x: x.get(sort, ""), reverse=reverse)
            except Exception:
                pass
        
        # 分页或切片
        if page is not None and limit is not None:
            start = (page - 1) * limit
            end = start + limit
        elif start is not None:
            end = end if end is not None else len(items)
        
        if start is not None and end is not None:
            items = items[start:end]
        
        return items
    
    def get_field(self, item_id: Any, field: str) -> Any:
        """获取数据项的特定字段"""
        item = self.get_item(item_id)
        if item:
            return item.get(field)
        return None
    
    def set_field(self, item_id: Any, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """设置数据项的特定字段"""
        return self.update_item(item_id, {field: value}, partial=True)
