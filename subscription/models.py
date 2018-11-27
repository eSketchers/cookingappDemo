import datetime

from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings

User = settings.AUTH_USER_MODEL


class StripeUser(models.Model):
    user = models.ForeignKey(User,
                             related_name='stripe_user',
                             verbose_name='User',
                             on_delete=models.SET_NULL,
                             null=True
                             )
    customer = models.CharField(max_length=255)

    def __str__(self):
        if self.user:
            return self.user.email
        return self.customer


class SubscriptionPlan(models.Model):
    MONTHLY = 'MON'
    SIX_MONTH = 'SIX_MON'
    ANNUAL = 'AN'
    FREE = 'FR'
    CUSTOM = 'CUSTOM'

    PLAN_TYPE_CHOICES = (
        (MONTHLY, 'MON'),
        (SIX_MONTH,'SIX_MON'),
        (ANNUAL, 'AN'),
        (FREE, 'FR'),
        (CUSTOM, 'CUSTOM'),
    )

    name = models.CharField(default='', max_length=255, blank=False, null=False)
    description = models.CharField(default='', max_length=255, blank=False, null=False)
    # prod_id = models.CharField(default='', max_length=255, blank=False, null=False, help_text="stripe product id which holds different plans")
    plan_id = models.CharField(default='', max_length=255, blank=False, null=False, help_text="stripe plan id")
    price = models.FloatField(default=0, null=False, blank=False)
    type = models.CharField(
        max_length=255,
        choices=PLAN_TYPE_CHOICES,
        default=FREE,
        help_text="Insert type of the plan, options samples: monthly, annual etc"
    )
    duration = models.IntegerField(default=settings.TRIAL_DAYS, validators=[
            MaxValueValidator(365),
            MinValueValidator(0)
        ])

    status = models.BooleanField(default=True, help_text='check this to show the plan to user')
    cancelable = models.BooleanField(default=True, help_text='if plan can be canceled or not')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['-id']

    def delete(self, using=None, keep_parents=False):
        if self.type == self.FREE:
            return None
        super(SubscriptionPlan, self).delete()


class Subscription(models.Model):
    user = models.ForeignKey(User,
                             related_name='subscription',
                             verbose_name='User',
                             on_delete=models.CASCADE,
                             )
    plan = models.ForeignKey('SubscriptionPlan',
                             related_name='subscription',
                             on_delete=models.PROTECT
                             )

    subscription = models.CharField(max_length=255, verbose_name='stripe_subscription_id', null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + ' ' + self.plan.name

    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expiry_date = timezone.now() + datetime.timedelta(days=self.plan.duration)
        super(Subscription, self).save(*args, **kwargs)


class SubscriptionLogs(models.Model):
    """
    maintain subscription logs against stripe webhooks
    """
    user = models.ForeignKey(User,
                             related_name='subscription_log_user',
                             verbose_name='User',
                             on_delete=models.SET_NULL,
                             null=True
                             )
    plan = models.CharField(default='', max_length=255, blank=False, null=True)
    subscription = models.CharField(default='', max_length=255, blank=False, null=True)

    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self. subscription + ' ' + self.plan

    class Meta:
        verbose_name = 'Subscription Log'
        verbose_name_plural = 'Subscriptions Logs'
        ordering = ['-created_at']


class EventLogs(models.Model):
    """
    maintain events(stripe webhoolk) logs
    """
    name = models.CharField(default='', max_length=255, blank=False, null=True)
    payload = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self. name

    class Meta:
        verbose_name = 'Event Log'
        verbose_name_plural = 'Events Logs'
        ordering = ['-created_at']