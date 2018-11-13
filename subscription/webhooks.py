import json

import logging
import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import subscription.models as subscription_app

# Get an instance of a logger
logger = logging.getLogger(__name__)

User = get_user_model()

stripe_events = {
    'payment_failed': 'invoice.payment_failed',
    'payment_succeeded': 'invoice.payment_succeeded',
    'invoice_created': 'invoice.created',
    'subscription_deleted': 'customer.subscription.deleted',
    'subscription_updated': 'customer.subscription.updated'
}




class WebHooksView(APIView):
    payload = {}

    def post(self, request, *args, **kwargs):
        """
        handle all stripe webhook here based on webhook/event type
        :param request:
        :param args:
        :param kwargs:
        :return: return status, either 200 or any other valid http statusto stripe if ok otherwise return
        """
        data = self.extract_json()
        status_code = 200

        event_type = None
        try:
            event_type = data['type']
            subscription_app.EventLogs.objects.create(name=event_type, payload=data)
            if event_type == stripe_events.get('subscription_deleted'):
                status_code = self.subscription_deleted(data)
        except Exception as e:
            logger.error('webhook event log error')
        # if event_type:
        # if data['type'] == stripe_events.get('payment_failed'):
        #     self.failed_payment(data)
        # elif data['type'] == stripe_events.get('subscription_deleted'):
        #     self.subscription_deleted(data)
        # elif data['type'] == stripe_events.get('payment_succeeded'):
        #     self.payment_succeed(data)
        # elif data['type'] == stripe_events.get('invoice.created'):
        #     self.invoice_created(data)
        # elif data['type'] == stripe_events.get('subscription_updated'):
        #     self.subscription_update(data)

        # result = self.save_webhook(data)
        return Response("request handled", status=status_code)

    def subscription_deleted(self, data):
        """
        handle stripe webhook for subscription deletion
        :param data: request.body in json format
        :return: status (eg. 200, 400) to be returned to stripe
        """

        type = stripe_events.get('subscription_deleted')
        verify_status = self.verify_signature(self.request, 'subscription_deleted')
        try:
            return verify_status
        finally:
            if verify_status == 200:
                # get customer id from stripe webhook call
                customer = data['data']['object']['customer']

                # check if user exists against customer
                customer_info = subscription_app.StripeUser.objects.filter(customer=customer).first()
                user = None

                if not customer_info:
                    try:
                        stripe_customer = stripe.Customer.retrieve(customer)
                        email = stripe_customer.email
                        user = User.objects.filter(email=email).first()

                        # save customer id for logs
                        subscription_app.StripeUser.objects.create(user=user, customer=customer)
                    except Exception as e:
                        logger.error('customer retrieve error')
                else:
                    user = customer_info.user

                # check if user exists agains this customer id.
                # user could not be in our db due to duplicated entries being rejected by our system during zaps receive
                if user:
                    # cancel user subscription
                    # save logs
                    self.cancel_sub_and_log(user,)

    def cancel_sub_and_log(self, user):
        subscription = user.subscription.filter(is_active=True).first()
        if subscription:
            subscription.is_active = False
            try:
                sub_log = subscription_app.SubscriptionLogs.objects.create(user=user,
                                                                           subscription=subscription.subscription,
                                                                           plan=subscription.plan.plan_id
                                                                           )
                subscription.save()
                sub_log.save()
            except Exception as e:
                logger.error('subscription log error', e)

    def extract_json(self):
        data = json.loads(smart_str(self.request.body))
        return data

    def verify_signature(self, request, type):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.endpoint_secret.get(type)
            )
        except ValueError as e:
            # Invalid payload
            return 400
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return 400
        except Exception as e:
            return 400

        # verified
        return 200
