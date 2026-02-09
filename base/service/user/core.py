"""
用户管理核心逻辑
- 本地用户：用户名+密码哈希，本地验证
- OAuth2 用户：OAuth2 验证，本地保存用户信息
- 密码：SHA256 预处理后 bcrypt 散列，支持任意长度
"""
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from passlib.context import CryptContext
from service.jsonserv.core import JSONDataStore

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 角色定义
ROLE_ADMIN = "admin"   # 管理员
ROLE_USER = "user"     # 用户
ROLES = [ROLE_ADMIN, ROLE_USER]
ROLE_LABELS = {ROLE_ADMIN: "管理员", ROLE_USER: "用户"}

_user_service: Optional["UserService"] = None


def get_user_service(config=None) -> "UserService":
    """获取用户服务单例"""
    global _user_service
    if _user_service is None:
        if config is None:
            from module.config import Config
            config = Config()
        _user_service = UserService(config)
    return _user_service


class UserService:
    """用户管理服务"""
    
    def __init__(self, config):
        self.config = config
        base_dir = Path(__file__).parent.parent.parent
        data_path = base_dir / config.get("jsonserv.data_path", "etc/data")
        users_file = data_path / "users.json"
        users_file.parent.mkdir(parents=True, exist_ok=True)
        if not users_file.exists():
            users_file.write_text('{"data": [], "primary_key": "id"}', encoding="utf-8")
        self.store = JSONDataStore(users_file, primary_key="id")
    
    def _password_to_bcrypt_input(self, password: str) -> str:
        """将任意长度密码转为 bcrypt 可接受格式：SHA256 散列后 64 字符，避免 72 字节限制"""
        if password is None:
            return ""
        try:
            pw_bytes = str(password).encode("utf-8")
            return hashlib.sha256(pw_bytes).hexdigest()
        except (UnicodeEncodeError, AttributeError):
            return ""

    def _hash_password(self, password: str) -> str:
        """密码哈希：SHA256 预处理 + bcrypt，支持任意长度，存 users.json 时已散列"""
        return pwd_context.hash(self._password_to_bcrypt_input(password))

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码。新：SHA256+bcrypt；旧用户兼容：直接 bcrypt"""
        bcrypt_input = self._password_to_bcrypt_input(plain_password)
        if pwd_context.verify(bcrypt_input, hashed_password):
            return True
        # 兼容旧数据：直接校验明文（仅当 ≤72 字节时）
        try:
            pw_bytes = (plain_password or "").encode("utf-8")
            if len(pw_bytes) <= 72:
                return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
        return False
    
    def get_users(self, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取用户列表"""
        items = self.store.get_items()
        if type_filter:
            items = [u for u in items if u.get("type") == type_filter]
        return items
    
    def get_user_by_id(self, user_id) -> Optional[Dict[str, Any]]:
        """根据 ID 获取用户"""
        return self.store.get_item(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        items = self.store.get_items()
        for u in items:
            if u.get("username") == username:
                return u
        return None
    
    def get_user_by_oauth2_sub(self, oauth2_sub: str) -> Optional[Dict[str, Any]]:
        """根据 OAuth2 sub 获取用户"""
        items = self.store.get_items()
        for u in items:
            if u.get("type") == "oauth2" and u.get("oauth2_sub") == oauth2_sub:
                return u
        return None
    
    def verify_local_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """验证本地用户，成功返回用户信息（不含密码）"""
        user = self.get_user_by_username(username)
        if not user or user.get("type") != "local":
            return None
        if not user.get("enabled", True):
            return None
        hashed = user.get("password_hash")
        if not hashed or not self._verify_password(password, hashed):
            return None
        return self._safe_user(user)
    
    def get_oauth2_user_by_match(self, userinfo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """根据 userinfo 匹配预注册的 OAuth2 用户（通过 username 或 email）"""
        oauth2_username = userinfo.get("username") or userinfo.get("user_name") or userinfo.get("name") or ""
        oauth2_email = userinfo.get("email") or ""
        items = self.store.get_items()
        for u in items:
            if u.get("type") != "oauth2":
                continue
            # 已绑定 oauth2_sub 的由 get_user_by_oauth2_sub 处理，这里只找预注册（无 oauth2_sub 或空）
            sub = u.get("oauth2_sub")
            if sub:
                continue
            if u.get("username") == oauth2_username:
                return u
            if oauth2_email and u.get("email") == oauth2_email:
                return u
        return None

    def get_or_create_oauth2_user(self, userinfo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        OAuth2 回调后获取用户
        登录验证由 OAuth2 完成，本系统权限查看 users.json：
        - 若 users.json 中已有该用户（oauth2_sub 或 预注册 username/email 匹配），则返回用户信息
        - 若不存在，返回 None（无权限）
        """
        oauth2_sub = str(userinfo.get("sub", userinfo.get("id", "")))
        username = userinfo.get("username") or userinfo.get("user_name") or userinfo.get("name") or oauth2_sub

        user = self.get_user_by_oauth2_sub(oauth2_sub)
        now = int(time.time())

        if user:
            # 已存在的 OAuth2 用户，更新信息
            user["display_name"] = userinfo.get("name") or user.get("display_name")
            user["email"] = userinfo.get("email") or user.get("email")
            user["oauth2_info"] = {k: v for k, v in userinfo.items() if k not in ("sub", "id")}
            user["updated_at"] = now
            self.store.update_item(user["id"], user, partial=True)
            return self._safe_user(user)

        # 查找预注册的 OAuth2 用户（通过 username 或 email 匹配）
        user = self.get_oauth2_user_by_match(userinfo)
        if user:
            # 绑定 oauth2_sub，完成首次登录
            user["oauth2_sub"] = oauth2_sub
            user["username"] = username
            user["display_name"] = userinfo.get("name") or user.get("display_name")
            user["email"] = userinfo.get("email") or user.get("email")
            user["oauth2_info"] = {k: v for k, v in userinfo.items() if k not in ("sub", "id")}
            user["updated_at"] = now
            self.store.update_item(user["id"], user, partial=True)
            return self._safe_user(user)

        # users.json 中无此用户，无本系统权限
        return None
    
    def create_oauth2_user(self, username: str, role: str = ROLE_USER) -> Dict[str, Any]:
        """创建 OAuth2 用户（预注册）。显示名、邮箱等信息由 OAuth2 在登录时同步，本系统仅维护用户名、角色"""
        if self.get_user_by_username(username):
            raise ValueError(f"用户名已存在: {username}")
        if role not in ROLES:
            role = ROLE_USER
        now = int(time.time())
        user = {
            "username": username,
            "type": "oauth2",
            "role": role,
            "oauth2_sub": "",  # 首次 OAuth2 登录后绑定
            "enabled": True,
            "created_at": now,
            "updated_at": now,
        }
        return self._safe_user(self.store.add_item(user))

    def create_local_user(self, username: str, password: str, display_name: str = "", email: str = "", role: str = ROLE_USER) -> Dict[str, Any]:
        """创建本地用户"""
        if self.get_user_by_username(username):
            raise ValueError(f"用户名已存在: {username}")
        if role not in ROLES:
            role = ROLE_USER
        now = int(time.time())
        user = {
            "username": username,
            "type": "local",
            "role": role,
            "password_hash": self._hash_password(password),
            "display_name": display_name or username,
            "email": email,
            "enabled": True,
            "created_at": now,
            "updated_at": now,
        }
        return self._safe_user(self.store.add_item(user))
    
    def update_local_user_password(self, user_id, new_password: str) -> Optional[Dict[str, Any]]:
        """更新本地用户密码"""
        user = self.store.get_item(user_id)
        if not user or user.get("type") != "local":
            return None
        user["password_hash"] = self._hash_password(new_password)
        user["updated_at"] = int(time.time())
        return self.store.update_item(user_id, user, partial=True)
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户（不含密码）。OAuth2 用户的 display_name、email 等由 OAuth2 管理，不可本地修改"""
        user = self.store.get_item(user_id)
        if not user:
            return None
        # 禁止修改的字段
        forbidden = ["password_hash", "oauth2_sub", "type", "id"]
        if user.get("type") == "oauth2":
            forbidden.extend(["display_name", "email", "oauth2_info", "username"])
        for key in forbidden:
            data.pop(key, None)
        data["updated_at"] = int(time.time())
        updated = self.store.update_item(user_id, data, partial=True)
        return self._safe_user(updated) if updated else None
    
    def delete_user(self, user_id) -> bool:
        """删除用户"""
        return self.store.delete_item(user_id)
    
    def _safe_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """返回安全的用户信息（不含密码哈希）"""
        safe = {k: v for k, v in user.items() if k != "password_hash"}
        return safe
