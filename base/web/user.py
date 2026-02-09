"""
用户管理 API
处理 /api/user/* 请求
"""
import json
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from service.user import get_user_service

logger = logging.getLogger("baseplatform.user")


async def handle(request: Request):
    """用户管理入口"""
    sub_path = getattr(request.state, "sub_path", "").strip("/")
    parts = sub_path.split("/") if sub_path else []
    
    user_service = get_user_service(getattr(request.app.state, "config", None))
    
    # POST /api/user/login - 本地登录
    if request.method == "POST" and sub_path == "login":
        return await login(request, user_service)
    
    # GET /api/user - 用户列表
    if request.method == "GET" and (not parts or parts[0] == "list"):
        return await list_users(request, user_service)
    
    # POST /api/user - 创建用户
    if request.method == "POST" and not parts:
        return await create_user(request, user_service)
    
    # GET/PUT/DELETE /api/user/{id}
    if parts and parts[0].isdigit():
        user_id = int(parts[0])
        if request.method == "GET":
            return await get_user(user_id, user_service)
        if request.method == "PUT" or request.method == "PATCH":
            return await update_user(user_id, request, user_service)
        if request.method == "DELETE":
            return await delete_user(user_id, user_service)
    
    # PUT /api/user/{id}/password - 修改本地用户密码
    if len(parts) >= 2 and parts[0].isdigit() and parts[1] == "password":
        if request.method == "PUT" or request.method == "POST":
            return await update_password(int(parts[0]), request, user_service)
    
    return JSONResponse(status_code=404, content={"detail": "未知接口"})


async def login(request: Request, user_service) -> JSONResponse:
    """本地用户登录"""
    try:
        data = await request.json()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if not username or not password:
            return JSONResponse(status_code=400, content={"detail": "用户名和密码不能为空"})
        user = user_service.verify_local_user(username, password)
        if not user:
            return JSONResponse(status_code=401, content={"detail": "用户名或密码错误"})
        config = getattr(request.app.state, "config", None)
        token = None
        if config:
            from jose import jwt
            import time
            secret = config.get("security.secret_key", "change-me")
            algo = config.get("security.algorithm", "HS256")
            expire_min = config.get("security.access_token_expire_minutes", 30)
            payload = {"sub": str(user.get("id", "")), "username": user.get("username", ""), "role": user.get("role", "user"), "exp": int(time.time()) + expire_min * 60, "iat": int(time.time())}
            token = jwt.encode(payload, secret, algorithm=algo)
        resp = {"success": True, "message": "登录成功", "user": user, "token": token, "token_type": "Bearer"}
        logger.info(f"本地登录成功: user={user.get('username')}")
        return JSONResponse(content=resp)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


async def list_users(request: Request, user_service) -> JSONResponse:
    """获取用户列表"""
    try:
        type_filter = request.query_params.get("type")
        users = user_service.get_users(type_filter=type_filter)
        return JSONResponse(content={"data": users})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


async def create_user(request: Request, user_service) -> JSONResponse:
    """创建用户"""
    try:
        data = await request.json()
        user_type = data.get("type", "local")
        username = (data.get("username") or "").strip()
        if not username:
            return JSONResponse(status_code=400, content={"detail": "用户名不能为空"})
        
        if user_type == "local":
            password = data.get("password") or ""
            if not password:
                return JSONResponse(status_code=400, content={"detail": "本地用户密码不能为空"})
            role = data.get("role", "user")
            user = user_service.create_local_user(
                username=username,
                password=password,
                display_name=data.get("display_name", ""),
                email=data.get("email", ""),
                role=role
            )
        elif user_type == "oauth2":
            username = (data.get("username") or "").strip()
            if not username:
                return JSONResponse(status_code=400, content={"detail": "OAuth2 用户名不能为空"})
            user = user_service.create_oauth2_user(
                username=username,
                role=data.get("role", "user")
            )
        else:
            return JSONResponse(status_code=400, content={"detail": f"不支持的用户类型: {user_type}"})
        
        return JSONResponse(content={"success": True, "user": user})
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


async def get_user(user_id: int, user_service) -> JSONResponse:
    """获取单个用户"""
    user = user_service.get_user_by_id(user_id)
    if not user:
        return JSONResponse(status_code=404, content={"detail": "用户不存在"})
    return JSONResponse(content=user_service._safe_user(user))


async def update_user(user_id: int, request: Request, user_service) -> JSONResponse:
    """更新用户"""
    try:
        data = await request.json()
        updated = user_service.update_user(user_id, data)
        if not updated:
            return JSONResponse(status_code=404, content={"detail": "用户不存在"})
        return JSONResponse(content={"success": True, "user": updated})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


async def delete_user(user_id: int, user_service) -> JSONResponse:
    """删除用户"""
    if not user_service.delete_user(user_id):
        return JSONResponse(status_code=404, content={"detail": "用户不存在"})
    return JSONResponse(content={"success": True, "message": "删除成功"})


async def update_password(user_id: int, request: Request, user_service) -> JSONResponse:
    """更新本地用户密码"""
    try:
        data = await request.json()
        new_password = data.get("password") or data.get("new_password") or ""
        if not new_password:
            return JSONResponse(status_code=400, content={"detail": "新密码不能为空"})
        updated = user_service.update_local_user_password(user_id, new_password)
        if not updated:
            return JSONResponse(status_code=404, content={"detail": "用户不存在或非本地用户"})
        return JSONResponse(content={"success": True, "message": "密码已更新"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
