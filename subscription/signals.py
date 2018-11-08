import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from subscription.models import SubscriptionPlan, Subscription

User = settings.AUTH_USER_MODEL


# FORMAT = '%(asctime)-15s %(user)s -8s %(message)s'
# logging.basicConfig(format=FORMAT)

# Get an instance of a logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            plan_id = instance._plan_id
            sub_id = instance._sub_id
            plan = SubscriptionPlan.objects.filter(plan_id=plan_id).first()
            if not plan:
                # try to subscribe to free plan
                plan = SubscriptionPlan.objects.filter(type=SubscriptionPlan.FREE).first()
                if plan:
                    Subscription.objects.create(user=instance, plan=plan, is_active=True)
            else:
                Subscription.objects.create(user=instance, plan=plan, subscription=sub_id, is_active=True)

        except Exception as e:
            try:
                plan = SubscriptionPlan.objects.get(type=SubscriptionPlan.FREE)
                Subscription.objects.create(user=instance, plan=plan, is_active=True)
            except SubscriptionPlan.DoesNotExist as e:
                print('plan does not exist')
                logger.error("plan does not exist, subscription not created for -{0}".format(instance.email))
                # dic = {'user': instance.email, 'error': ''}
                # logger.error('user create signal: %s', 'plan does not exits', extra=dic)
                # logger.error(e, extra={})
            except Exception as e:
                print(e)
                logger.error("subscription not created for -{0} -- {1}".format(instance.email, e.args))
                # dic = {'user': instance.email, 'error': e.args}
                # logger.error('user create signal: %s', 'get plan & subscribe error', extra=dic)