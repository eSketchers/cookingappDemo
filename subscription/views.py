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
        return SubscriptionPlan.objects.filter(is_active=True) \
            .exclude(type=SubscriptionPlan.FREE) \
            .exclude(status=False)


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


class CancelSubscriptionApiView(APIView):
    """
    API View to subscribe user to stripe plan.
    """
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user_sub = request.user.subscription.filter(is_active=True).first()
        if user_sub:
            if user_sub.plan.type != SubscriptionPlan.FREE:
                message = "Subscription could not be canceled"
                try:
                    stripe_sub_id = user_sub.subscription
                    stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
                    stripe_sub.delete()
                    # user_sub.is_active = False
                    # user_sub.save()
                    return Response({'success': True, 'message': 'Subscription has been canceled'},
                                    status=status.HTTP_200_OK)
                except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    # message = e.user_message
                    message = "Subscription not found."
                except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    message = 'Service is not available.'
                except stripe.error.APIConnectionError as e:
                    # Network communication with Stripe failed
                    message = "Network Communication Error."
                except stripe.error.StripeError as e:
                    message = "Payment service is not responding. Please try again later."
                except Exception as e:
                    message = 'Subscription could not be canceled. Please try again and contact admin if it still does not cancel'

                return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

            # user_sub.is_active = False
            # user_sub.save()
            return Response({'success': True, 'message': 'Subscription has been canceled'}, status=status.HTTP_200_OK)

        return Response({'success': True, 'message': 'No active subscription found'}, status=status.HTTP_200_OK)