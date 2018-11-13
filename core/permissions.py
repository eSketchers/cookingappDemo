from rest_framework import permissions


class HasActiveSubscription(permissions.BasePermission):
    message = 'You are not subscribed to a plan.'

    def has_permission(self, request, view):
        user = request.user
        return user.subscription.filter(is_active=True).exists()
        # return True
