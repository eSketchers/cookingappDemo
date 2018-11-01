from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from subscription.models import SubscriptionPlan, Subscription

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        plan = SubscriptionPlan.objects.get(type='FR')
        if plan:
            subscription = Subscription.objects.create(user=instance, plan=plan, is_active=True)
            subscription.save()
