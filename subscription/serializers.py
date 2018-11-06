import logging
import stripe
from django.conf import settings
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import *

stripe.api_key = settings.STRIPE_SECRET_API_KEY

# Get an instance of a logger
logger = logging.getLogger(__name__)


class SubscriptionSerializer(serializers.ModelSerializer):
    # user = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = Subscription
        depth = 1
        # fields = '__all__'
        exclude = ('user', )


class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class TokenSerializer(serializers.Serializer):
    plan_id = serializers.CharField(max_length=255, required=True)
    token = serializers.CharField(max_length= 255, required=True)

    def validate_plan_id(self, value):
        return get_object_or_404(SubscriptionPlan, pk=value)

    def create(self, validated_data):
        payload = {}
        try:
            plan = validated_data.get('plan_id')
            token = validated_data.get('token')
            user = self.context['request'].user

            check_subscription = Subscription.objects.filter(user=user, is_active=True).exclude(plan__type=SubscriptionPlan.FREE).first()
            if not check_subscription:
                customer_info = StripeUser.objects.filter(user=user).first()
                customer_id = None
                if not customer_info:
                    customer = stripe.Customer.create(
                        description="Customer for Dropship CEO",
                        source=token,
                        email=user.email
                    )
                    customer_id = customer.id
                    StripeUser.objects.create(user=user, customer=customer_id)
                else:
                    customer_id = customer_info.customer

                stripe_subscription = stripe.Subscription.create(
                    customer=customer_id,
                    items=[
                        {
                            "plan": plan.plan_id,
                        },
                    ]
                )

                Subscription.objects.filter(user=user, is_active=True).update(is_active=False)
                Subscription.objects.create(user=user, plan=plan, subscription=stripe_subscription.id, is_active=True)
                return {'data': {'success': True, 'message': 'You have successfully subscribed.'},
                        'status': status.HTTP_200_OK}

            else:
                return {'data': {'success': True, 'message': 'You are already subscribed to this plan.'},
                        'status': status.HTTP_200_OK}

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            payload.update({'error': e.user_message})
            payload.update({'success': False})
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            payload.update({'error': 'Service is not available.'})
            payload.update({'success': False})
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            payload.update({'error': "Network Communication Error."})
            payload.update({'success': False})
        except stripe.error.StripeError as e:
            payload.update({'error': "Error from payment service."})
            payload.update({'success': False})
        except Exception as e:
            payload.update({'error': e.message})
            payload.update({'success': False})

        logger.error('subscription create error', )
        return {'data': {'success': payload['success'], 'errors': payload['error']}, 'status': status.HTTP_400_BAD_REQUEST}
        # return Response({'success': payload['success'], 'errors': payload['error']}, status=status.HTTP_400_BAD_REQUEST)
