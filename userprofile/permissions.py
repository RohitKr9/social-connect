from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user

class CanViewProfile(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.can_view_profile(request.user)

class IsAdminOrOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user