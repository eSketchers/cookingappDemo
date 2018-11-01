from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from subscription.models import Subscription
from subscription.serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Subscription.objects.filter(is_active=True, user=self.request.user)
