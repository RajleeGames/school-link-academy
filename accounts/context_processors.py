# accounts/context_processors.py

from .permissions import get_role_permissions, get_user_role, user_has_permission


def account_permissions_context(request):
    user = getattr(request, "user", None)

    role = get_user_role(user)
    permissions = get_role_permissions(role)

    return {
        "current_user_role": role,
        "current_user_permissions": permissions,
        "can": lambda code: user_has_permission(user, code),
    }