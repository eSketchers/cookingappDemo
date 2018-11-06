from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from subscription.models import Subscription, SubscriptionPlan
from subscription.serializers import SubscriptionSerializer, SubscriptionPlanSerializer, TokenSerializer

import stripe
stripe.api_key = settings.STRIPE_SECRET_API_KEY


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Subscription.objects.filter(is_active=True, user=self.request.user)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for subscriptions plans.
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated, ]
    # queryset = SubscriptionPlan.objects.all()

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True).exclude(type=SubscriptionPlan.FREE)


class SubscribeApiView(APIView):
    """
    API View to subscribe user to stripe plan.
    """
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = TokenSerializer(context={'request': request}, data=request.data)
        if serializer.is_valid():
            response = serializer.save()
            return Response(response['data'], status=response['status'])
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)