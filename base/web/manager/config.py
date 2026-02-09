"""
配置管理 API
处理 /api/manager/config/* 的请求
"""
from fastapi.responses import JSONResponse
from fastapi import Request


async def handle(request: Request):
    """配置管理入口"""
    sub_path = getattr(request.state, 'sub_path', '')

    if sub_path == 'oauth2':
        return await save_oauth2_config(request)
    else:
        return JSONResponse(
            status_code=404,
            content={"detail": f"未知的配置接口: {sub_path}"}
        )


async def save_oauth2_config(request: Request):
    """保存 OAuth2 配置"""
    import logging

    logger = logging.getLogger("manager.config")
    config = getattr(request.app.state, "config", None)
    if config is None:
        return JSONResponse(
            status_code=500,
            content={"detail": "配置模块未初始化，请检查 app.state.config 是否已设置"}
        )

    try:
        data = await request.json()

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

        config.update_oauth2_config(oauth2_config)

        return JSONResponse(content={
            "success": True,
            "message": "OAuth2 配置保存成功"
        })
    except Exception as e:
        import traceback
        logger.error(f"保存 OAuth2 配置失败: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"保存配置失败: {str(e)}",
                "traceback": traceback.format_exc()
            }
        )
