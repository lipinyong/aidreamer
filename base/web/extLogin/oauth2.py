"""
OAuth2 登录接口（extLogin 路径，供 OAuth2 回调 URL 使用）
委托给 login.oauth2 处理
"""
import importlib.util
from pathlib import Path

# 动态加载 login.oauth2 模块
_login_oauth2_path = Path(__file__).parent.parent / "login" / "oauth2.py"
_spec = importlib.util.spec_from_file_location("login_oauth2", _login_oauth2_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

async def handle(request):
    return await _mod.handle(request)
