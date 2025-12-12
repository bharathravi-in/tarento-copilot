"""Pydantic request/response schemas package"""

from .auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    PasswordChangeRequest,
    TokenResponse,
    TokenRefreshRequest,
    TokenPayload,
    AuthResponse,
)
from .organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
)
from .project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
)
from .role import (
    PermissionResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleDetailResponse,
    BulkPermissionAssign,
    BulkPermissionRevoke,
)

__all__ = [
    # Auth
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "PasswordChangeRequest",
    "TokenResponse",
    "TokenRefreshRequest",
    "TokenPayload",
    "AuthResponse",
    # Organization
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "OrganizationDetailResponse",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectDetailResponse",
    # Role & Permission
    "PermissionResponse",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleDetailResponse",
    "BulkPermissionAssign",
    "BulkPermissionRevoke",
]
