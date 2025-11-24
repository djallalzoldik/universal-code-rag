# Comprehensive Python test file with complex structures
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Generic, TypeVar
from threading import Lock
from enum import Enum

class Authenticator(ABC):
    """Abstract authenticator interface"""
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        pass
    
    @abstractmethod
    def logout(self) -> None:
        pass


@dataclass
class User(ABC):
    """Base user class with dataclass"""
    username: str
    id: int
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)
    
    @abstractmethod
    def get_role(self) -> str:
        pass


class AdminUser(User, Authenticator):
    """AdminUser with multiple inheritance"""
    
    def __init__(self, username: str, id: int):
        super().__init__(username=username, id=id)
        self._permissions: List[str] = []
    
    def get_role(self) -> str:
        return "ADMIN"
    
    def authenticate(self, username: str, password: str) -> bool:
        if not username or not password:
            return False
        return self.username == username and self._validate_password(password)
    
    def logout(self) -> None:
        print("Admin logged out")
    
    def add_permission(self, permission: str) -> None:
        with self._lock:
            self._permissions.append(permission)
    
    def get_permissions(self) -> List[str]:
        with self._lock:
            return self._permissions.copy()
    
    def _validate_password(self, password: str) -> bool:
        return len(password) >= 8


T = TypeVar('T', bound=User)

class SessionManager(Generic[T]):
    """Generic session manager using singleton pattern"""
    
    _instance: Optional['SessionManager'] = None
    _lock: Lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._sessions = {}
        return cls._instance
    
    def create_session(self, session_id: str, user: T) -> None:
        with self._lock:
            self._sessions[session_id] = user
    
    def get_session(self, session_id: str) -> Optional[T]:
        with self._lock:
            return self._sessions.get(session_id)
    
    def remove_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


class StatusCode(Enum):
    """Status code enum"""
    SUCCESS = 200
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    
    @property
    def message(self) -> str:
        messages = {
            StatusCode.SUCCESS: "OK",
            StatusCode.UNAUTHORIZED: "Unauthorized",
            StatusCode.FORBIDDEN: "Forbidden",
            StatusCode.NOT_FOUND: "Not Found",
        }
        return messages.get(self, "Unknown")


def authenticate_and_create_session(
    user: Authenticator,
    username: str,
    password: str,
    manager: SessionManager
) -> Dict[str, any]:
    """Complex function with type hints"""
    if user.authenticate(username, password):
        import uuid
        session_id = f"session_{uuid.uuid4()}"
        manager.create_session(session_id, user)
        return {"success": True, "session_id": session_id}
    return {"success": False, "error": StatusCode.UNAUTHORIZED.message}


# Context manager
class AuthenticationContext:
    """Context manager for authentication"""
    
    def __init__(self, user: Authenticator):
        self.user = user
    
    def __enter__(self):
        return self.user
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.user.logout()
        return False


# Decorator
def require_authentication(func):
    """Decorator for authentication requirement"""
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'authenticated') or not self.authenticated:
            raise PermissionError("Authentication required")
        return func(self, *args, **kwargs)
    return wrapper
