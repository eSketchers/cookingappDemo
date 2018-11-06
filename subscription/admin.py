from django.conf import settings
from django.contrib import admin

from subscription.models import SubscriptionPlan, Subscription, StripeUser


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'price', 'plan_id']
    exclude = ('', )
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        if obj.type == 'MON':
            obj.duration = 30
        elif obj.type == 'AN':
            obj.duration = 365
        else:
            obj.duration = settings.TRIAL_DAYS
        obj.save()

    def delete_model(self, request, obj):
        if obj.type == 'FR':
            return None
        super(SubscriptionPlanAdmin, self).delete_model(request, obj)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'expiry_date', 'is_active']
    exclude = ()
    # search_fields = ('title',)

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(StripeUser)
