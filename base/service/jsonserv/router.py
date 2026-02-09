"""
jsonserv 路由注册
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from service.jsonserv.core import JSONDataStore


logger = logging.getLogger("baseplatform.jsonserv")
stores: Dict[str, JSONDataStore] = {}


def scan_json_files(data_path: Path) -> Dict[str, Path]:
    """扫描 JSON 文件"""
    json_files = {}
    
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
        return json_files
    
    for json_file in data_path.rglob("*.json"):
        # 获取相对路径作为资源名
        relative_path = json_file.relative_to(data_path)
        resource_name = str(relative_path).replace("\\", "/").replace(".json", "")
        json_files[resource_name] = json_file
    
    return json_files


def setup_jsonserv(app: FastAPI, config) -> Dict[str, JSONDataStore]:
    """设置 jsonserv 路由"""
    base_dir = Path(__file__).parent.parent.parent
    data_path = base_dir / config.get("jsonserv.data_path", "etc/data")
    
    # 扫描 JSON 文件
    json_files = scan_json_files(data_path)
    exclude_resources = config.get("jsonserv.exclude_resources", [])
    
    # 为每个 JSON 文件创建数据存储和路由
    for resource_name, json_file in json_files.items():
        if resource_name in exclude_resources:
            logger.info(f"跳过 jsonserv 资源（已排除）: {resource_name}")
            continue
        try:
            # 加载 JSON 文件以确定主键
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 确定主键
            primary_key = "id"
            if isinstance(data, dict) and "primary_key" in data:
                primary_key = data["primary_key"]
            
            # 创建数据存储
            store = JSONDataStore(json_file, primary_key)
            stores[resource_name] = store
            
            # 注册路由
            register_routes(app, resource_name, store)
            
            logger.info(f"注册 jsonserv 资源: {resource_name}")
        
        except Exception as e:
            logger.error(f"加载 JSON 文件失败 {json_file}: {e}")
    
    return stores


def register_routes(app: FastAPI, resource_name: str, store: JSONDataStore):
    """为资源注册 CRUD 路由"""
    
    # GET /api/jsonserv/{resource_name} - 获取列表
    @app.get(f"/api/jsonserv/{resource_name}")
    async def get_list(
        page: Optional[int] = Query(None, alias="_page"),
        limit: Optional[int] = Query(None, alias="_limit"),
        sort: Optional[str] = Query(None, alias="_sort"),
        order: Optional[str] = Query("asc", alias="_order"),
        start: Optional[int] = Query(None, alias="_start"),
        end: Optional[int] = Query(None, alias="_end"),
        q: Optional[str] = Query(None),
    ):
        """获取资源列表"""
        # 获取查询参数作为过滤条件
        filters = {}
        # 这里需要从请求中获取所有非特殊参数作为过滤条件
        # 实际实现中需要从 Request 对象获取
        
        items = store.query(
            filters=filters,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
            start=start,
            end=end,
            search=q
        )
        return items
    
    # GET /api/jsonserv/{resource_name}/{id} - 获取单条数据
    @app.get(f"/api/jsonserv/{resource_name}/{{item_id}}")
    async def get_item(item_id: str):
        """获取单条数据"""
        item = store.get_item(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return item
    
    # POST /api/jsonserv/{resource_name} - 新增数据
    @app.post(f"/api/jsonserv/{resource_name}")
    async def create_item(item: Dict[str, Any]):
        """新增数据"""
        new_item = store.add_item(item)
        return new_item
    
    # PUT /api/jsonserv/{resource_name}/{id} - 全量更新
    @app.put(f"/api/jsonserv/{resource_name}/{{item_id}}")
    async def update_item(item_id: str, item: Dict[str, Any]):
        """全量更新"""
        updated_item = store.update_item(item_id, item, partial=False)
        if updated_item is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return updated_item
    
    # PATCH /api/jsonserv/{resource_name}/{id} - 局部更新
    @app.patch(f"/api/jsonserv/{resource_name}/{{item_id}}")
    async def patch_item(item_id: str, item: Dict[str, Any]):
        """局部更新"""
        updated_item = store.update_item(item_id, item, partial=True)
        if updated_item is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return updated_item
    
    # DELETE /api/jsonserv/{resource_name}/{id} - 删除数据
    @app.delete(f"/api/jsonserv/{resource_name}/{{item_id}}")
    async def delete_item(item_id: str):
        """删除数据"""
        success = store.delete_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="资源不存在")
        return {"message": "删除成功"}
    
    # GET /api/jsonserv/{resource_name}/{id}/{field} - 获取字段
    @app.get(f"/api/jsonserv/{resource_name}/{{item_id}}/{{field}}")
    async def get_field(item_id: str, field: str):
        """获取字段值"""
        value = store.get_field(item_id, field)
        if value is None:
            raise HTTPException(status_code=404, detail="字段不存在")
        return {field: value}
    
    # PUT /api/jsonserv/{resource_name}/{id}/{field} - 更新字段
    @app.put(f"/api/jsonserv/{resource_name}/{{item_id}}/{{field}}")
    async def set_field(item_id: str, field: str, value: Any):
        """更新字段值"""
        updated_item = store.set_field(item_id, field, value)
        if updated_item is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return updated_item
