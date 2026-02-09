"""
用户管理服务
支持本地用户和 OAuth2 用户，数据存储在 etc/data/users.json
使用 JSONDataStore（与 jsonserv 相同机制）进行读写
角色：admin(管理员)、user(用户)
"""
from .core import UserService, get_user_service, ROLES, ROLE_ADMIN, ROLE_USER, ROLE_LABELS

__all__ = ["UserService", "get_user_service", "ROLES", "ROLE_ADMIN", "ROLE_USER", "ROLE_LABELS"]
