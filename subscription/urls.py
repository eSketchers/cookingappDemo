from django.conf.urls import url, include
from .views import *

from rest_framework import routers

# Registration URLs
router = routers.SimpleRouter()
router.register(r'subscription', SubscriptionViewSet, 'Subscription')
router.register(r'plan', SubscriptionPlanViewSet, 'Plan')
urlpatterns = router.urls

urlpatterns += [

  url(r'^checkout/$', SubscribeApiView.as_view(), name='checkout'),
  # url(r'^delete-feed/(?P<pk>[0-9]+)/$', FavoriteFeeds.as_view(), name='delete-feed'),
]