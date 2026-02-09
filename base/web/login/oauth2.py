"""
OAuth2 登录接口
"""
import urllib.parse
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from module.config import Config
from module.logger import setup_logger

# 初始化配置和日志
config = Config()
logger = setup_logger(config)

async def GET(request: Request):
    """
    OAuth2 登录处理
    处理两种情况：
    1. /api/ExtLogin/oauth2 - 登录初始化，重定向到 OAuth2 服务器
    2. /api/extLogin/oauth2 - 回调处理，获取访问令牌并验证用户
    """
    # 获取当前路径，判断是初始化还是回调
    path = request.url.path
    if '/ExtLogin/' in path:
        # 登录初始化
        return await oauth2_login(request)
    else:
        # 回调处理
        return await oauth2_callback(request)

async def handle(request: Request):
    """
    处理请求
    根据请求方法调用相应的处理函数
    """
    if request.method == "GET":
        return await GET(request)
    else:
        raise HTTPException(status_code=405, detail="Method Not Allowed")

async def oauth2_login(request: Request):
    """
    OAuth2 登录初始化
    重定向用户到 OAuth2 服务器进行授权
    """
    try:
        # 获取 OAuth2 配置
        oauth2_config = config.get("oauth2", {})
        if not oauth2_config.get("enabled", False):
            raise HTTPException(status_code=400, detail="OAuth2 未启用")
        
        server_config = oauth2_config.get("server", {})
        client_config = oauth2_config.get("client", {})
        
        # 构建授权 URL
        authorize_url = f"{server_config.get('protocol', 'HTTPS')}://{server_config.get('host', '')}{server_config.get('authorize_path', '/oauth/v2/authorize')}"
        
        # 构建回调 URL
        callback_url = client_config.get('callback_url', '')
        if not callback_url:
            # 如果没有配置回调 URL，使用默认值
            callback_url = f"http://127.0.0.1:5000/api/login/oauth2"
        
        # 构建授权参数
        params = {
            "client_id": client_config.get('client_id', ''),
            "redirect_uri": callback_url,
            "response_type": "code",
            "scope": "read write",  # 根据实际需要调整 scope
            "state": "12345"  # 实际应用中应该使用随机生成的 state
        }
        
        # 构建完整的授权 URL
        full_authorize_url = f"{authorize_url}?{urllib.parse.urlencode(params)}"
        
        logger.info(f"OAuth2 登录重定向到: {full_authorize_url}")
        
        # 重定向用户到授权 URL
        return RedirectResponse(url=full_authorize_url)
    except Exception as e:
        logger.error(f"OAuth2 登录初始化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OAuth2 登录初始化失败: {str(e)}")

async def oauth2_callback(request: Request):
    """
    OAuth2 回调处理
    处理从 OAuth2 服务器返回的授权码，获取访问令牌并验证用户
    """
    try:
        # 检查 OAuth2 错误响应
        oauth_error = request.query_params.get("error")
        if oauth_error:
            desc = request.query_params.get("error_description", oauth_error)
            logger.warning(f"OAuth2 回调错误: {oauth_error} - {desc}")
            raise HTTPException(status_code=400, detail=f"OAuth2 授权失败: {desc}")

        # 获取授权码（部分 provider 使用 auth_code）
        code = request.query_params.get("code") or request.query_params.get("auth_code")
        if not code:
            # 若访问的是 /api/login/oauth2（无 code），重定向到发起授权
            path = request.url.path
            if "/login/oauth2" in path and "extLogin" not in path.lower():
                base = str(request.base_url).rstrip("/")
                init_url = f"{base}/api/ExtLogin/oauth2"
                return RedirectResponse(url=init_url)
            params = dict(request.query_params)
            logger.warning(f"OAuth2 回调缺少授权码, 收到参数: {params}")
            raise HTTPException(
                status_code=400,
                detail="缺少授权码。请确认：1) 回调 URL 与 OAuth2 配置一致 2) 从登录页点击 OAuth2 登录发起流程"
            )
        
        # 获取 OAuth2 配置
        oauth2_config = config.get("oauth2", {})
        server_config = oauth2_config.get("server", {})
        client_config = oauth2_config.get("client", {})
        
        # 构建回调 URL
        callback_url = client_config.get('callback_url', '')
        if not callback_url:
            callback_url = f"http://127.0.0.1:5000/api/extLogin/oauth2"
        
        # 构建获取访问令牌的请求
        import aiohttp
        token_url = f"{server_config.get('protocol', 'HTTPS')}://{server_config.get('host', '')}{server_config.get('token_path', '/oauth/v2/token')}"
        
        async with aiohttp.ClientSession() as session:
            # 发送请求获取访问令牌
            async with session.post(token_url, data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_config.get('client_id', ''),
                "client_secret": client_config.get('client_secret', ''),
                "redirect_uri": callback_url
            }) as response:
                token_data = await response.json()
                
                if "error" in token_data:
                    logger.error(f"获取访问令牌失败: {token_data}")
                    raise HTTPException(status_code=400, detail=f"获取访问令牌失败: {token_data.get('error_description', token_data.get('error'))}")
                
                # 获取访问令牌
                access_token = token_data.get("access_token")
                if not access_token:
                    raise HTTPException(status_code=400, detail="获取访问令牌失败")
                
                # 使用访问令牌获取用户信息
                userinfo_url = f"{server_config.get('protocol', 'HTTPS')}://{server_config.get('host', '')}{server_config.get('userinfo_path', '/oauth/v2/me')}"
                
                async with session.get(userinfo_url, headers={
                    "Authorization": f"Bearer {access_token}"
                }) as userinfo_response:
                    userinfo = await userinfo_response.json()
                    
                    if "error" in userinfo:
                        logger.error(f"获取用户信息失败: {userinfo}")
                        raise HTTPException(status_code=400, detail=f"获取用户信息失败: {userinfo.get('error_description', userinfo.get('error'))}")
        
        logger.info(f"OAuth2 验证成功，用户信息: {userinfo}")
        
        # 本系统权限由 users.json 控制，需先在用户管理中预注册
        from service.user import get_user_service
        user_service = get_user_service()
        user = user_service.get_or_create_oauth2_user(userinfo)
        
        if user is None:
            raise HTTPException(status_code=403, detail="该用户在本系统中无权限，请联系管理员在用户管理中添加 OAuth2 用户")
        
        resp = {
            "success": True,
            "message": "OAuth2 登录成功",
            "user": user,
            "userinfo": userinfo,
            "token": access_token,
            "token_type": token_data.get("token_type", "Bearer"),
        }
        if token_data.get("expires_in") is not None:
            resp["expires_in"] = token_data["expires_in"]
        if token_data.get("refresh_token"):
            resp["refresh_token"] = token_data["refresh_token"]
        logger.info(f"OAuth2 登录成功: user={user.get('username')}")
        return JSONResponse(content=resp)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth2 回调处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OAuth2 回调处理失败: {str(e)}")
