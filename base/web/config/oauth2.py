"""
OAuth2 配置接口
"""
import json
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from module.config import Config
from module.logger import setup_logger

# 初始化配置和日志
config = Config()
logger = setup_logger(config)

async def POST(request: Request):
    """
    保存 OAuth2 配置
    """
    try:
        data = await request.json()
        
        # 构建 OAuth2 配置结构
        oauth2_config = {
            "enabled": data.get("enabled", False),
            "server": {
                "host": data.get("server", {}).get("host", ""),
                "protocol": data.get("server", {}).get("protocol", "HTTPS"),
                "authorize_path": data.get("server", {}).get("authorize_path", "/oauth/v2/authorize"),
                "token_path": data.get("server", {}).get("token_path", "/oauth/v2/token"),
                "resource_path": data.get("server", {}).get("resource_path", "/oauth/v2/resource"),
                "userinfo_path": data.get("server", {}).get("userinfo_path", "/oauth/v2/me")
            },
            "client": {
                "client_id": data.get("client", {}).get("client_id", ""),
                "client_secret": data.get("client", {}).get("client_secret", ""),
                "callback_url": data.get("client", {}).get("callback_url", ""),
                "logout_callback_url": data.get("client", {}).get("logout_callback_url", "")
            },
            "login": {
                "button_text": data.get("login", {}).get("button_text", "使用 OAuth2 登录")
            },
            "admin": {
                "oauth2_protocol": data.get("admin", {}).get("oauth2_protocol", "HTTPS"),
                "oauth2_userinfo_path": data.get("admin", {}).get("oauth2_userinfo_path", "/oauth/v2/me")
            }
        }
        
        # 更新配置
        config.update_oauth2_config(oauth2_config)
        
        return JSONResponse(content={
            "success": True,
            "message": "OAuth2 配置保存成功"
        })
    except Exception as e:
        logger.error(f"保存 OAuth2 配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

async def handle(request: Request):
    """
    处理请求
    根据请求方法调用相应的处理函数
    """
    if request.method == "POST":
        return await POST(request)
    else:
        raise HTTPException(status_code=405, detail="Method Not Allowed")
