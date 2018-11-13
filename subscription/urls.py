from django.conf.urls import url, include

from subscription.webhooks import WebHooksView
from .views import *

from rest_framework import routers

# Registration URLs
router = routers.SimpleRouter()
router.register(r'subscription', SubscriptionViewSet, 'Subscription')
router.register(r'plan', SubscriptionPlanViewSet, 'Plan')
urlpatterns = router.urls

urlpatterns += [

  url(r'^checkout/$', SubscribeApiView.as_view(), name='checkout'),
  url(r'^cancel-subscription/$', CancelSubscriptionApiView.as_view(), name='checkout'),


  url(r'^s/webhook/$', WebHooksView.as_view(), name='stripe-webhook'),
  # url(r'^delete-feed/(?P<pk>[0-9]+)/$', FavoriteFeeds.as_view(), name='delete-feed'),
]
