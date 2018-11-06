from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from subscription.models import SubscriptionPlan, Subscription

User = get_user_model()


class Command(BaseCommand):
    help = 'Assign free subscription to existing users'

    def handle(self, *args, **kwargs):

        # users = EmailAddress.objects.all(user__is_admin=False, user__is_active=True, verified=True)
        users = User.objects.filter(is_admin=False)
        try:
            plan = SubscriptionPlan.objects.get(type=SubscriptionPlan.FREE)
            for user in users:
                if not Subscription.objects.filter(user=user).exists():
                    Subscription.objects.create(user=user, plan=plan, is_active=True)
        except SubscriptionPlan.DoesNotExist as e:
            print('code broke')