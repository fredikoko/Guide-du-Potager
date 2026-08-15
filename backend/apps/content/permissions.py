from rest_framework import permissions

class CanAccessChapterContent(permissions.BasePermission):
    """
    Custom permission to check if user has access to premium chapters.
    """
    def has_object_permission(self, request, view, obj):
        # If chapter/part is not premium, anyone can access
        if not obj.is_premium and not obj.part.is_premium:
            return True

        # If chapter/part is premium, user must be logged in and have active subscription
        user = request.user
        if user and user.is_authenticated and hasattr(user, 'profile'):
            return user.profile.subscription_active
        return False
