"""
Authorization Middleware and Helpers
Provides fine-grained access control and permission checking
"""

from typing import Optional, List, Callable
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from functools import wraps


class PermissionChecker:
    """Helper class for checking permissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def user_has_permission(self, user_id: str, permission_name: str) -> bool:
        """Check if user has specific permission"""
        from app.models import User, Permission
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return False
        
        if user.is_superuser:
            return True
        
        if not user.role:
            return False
        
        permission = self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        
        if not permission:
            return False
        
        return permission in user.role.permissions
    
    def user_has_any_permission(
        self,
        user_id: str,
        permission_names: List[str]
    ) -> bool:
        """Check if user has any of the specified permissions"""
        return any(
            self.user_has_permission(user_id, perm)
            for perm in permission_names
        )
    
    def user_has_all_permissions(
        self,
        user_id: str,
        permission_names: List[str]
    ) -> bool:
        """Check if user has all of the specified permissions"""
        return all(
            self.user_has_permission(user_id, perm)
            for perm in permission_names
        )


class ResourceAccessChecker:
    """Helper class for checking resource-level access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def user_can_access_organization(
        self,
        user_id: str,
        organization_id: str
    ) -> bool:
        """Check if user can access organization"""
        from app.models import User
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Superusers can access any organization
        if user.is_superuser:
            return True
        
        # Regular users can only access their organization
        return user.organization_id == organization_id
    
    def user_is_project_member(
        self,
        user_id: str,
        project_id: str
    ) -> bool:
        """Check if user is a member of project"""
        from app.models import Project
        
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            return False
        
        # Check if user is in project members
        return any(u.id == user_id for u in project.members)
    
    def user_is_project_creator(
        self,
        user_id: str,
        project_id: str
    ) -> bool:
        """Check if user created the project"""
        from app.models import Project
        
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            return False
        
        return project.created_by == user_id
    
    def user_can_manage_project(
        self,
        user_id: str,
        project_id: str
    ) -> bool:
        """Check if user can manage project (creator or admin)"""
        from app.models import User, Project
        
        user = self.db.query(User).filter(User.id == user_id).first()
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not user or not project:
            return False
        
        # Superuser can manage any project
        if user.is_superuser:
            return True
        
        # Admin can manage projects in their org
        if (user.role and user.role.name.lower() == 'admin' and
            user.organization_id == project.organization_id):
            return True
        
        # Creator can manage their own project
        return project.created_by == user_id


async def check_permission_dependency(
    permission_name: str,
    user = None,
    db: Session = None
):
    """
    Dependency function for checking permissions in route handlers
    
    Usage:
        @router.post("/users/")
        async def create_user(
            user_data: UserCreate,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db),
            _ = Depends(lambda: check_permission_dependency("user:create", current_user, db))
        ):
            pass
    """
    if not user or not db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    
    checker = PermissionChecker(db)
    if not checker.user_has_permission(user.id, permission_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {permission_name}"
        )
    
    return True


def enforce_organization_access(
    user_org_id: str,
    target_org_id: str,
    is_superuser: bool = False
) -> bool:
    """
    Enforce organization-level access control
    
    Args:
        user_org_id: User's organization ID
        target_org_id: Target organization ID
        is_superuser: Whether user is superuser
        
    Returns:
        True if access is allowed
        
    Raises:
        HTTPException: If access is denied
    """
    if is_superuser:
        return True
    
    if user_org_id != target_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access resources in your organization"
        )
    
    return True


def enforce_resource_ownership(
    user_id: str,
    owner_id: str,
    is_superuser: bool = False,
    is_admin: bool = False,
    same_org: bool = False
) -> bool:
    """
    Enforce resource ownership or admin privileges
    
    Args:
        user_id: User's ID
        owner_id: Resource owner's ID
        is_superuser: Whether user is superuser
        is_admin: Whether user is admin
        same_org: Whether to check organization membership
        
    Returns:
        True if access is allowed
        
    Raises:
        HTTPException: If access is denied
    """
    if is_superuser:
        return True
    
    if is_admin and same_org:
        return True
    
    if user_id == owner_id:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: You don't have permission to perform this action"
    )
