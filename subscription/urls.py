from django.conf.urls import url, include
from .views import *

from rest_framework import routers

# Registration URLs
router = routers.SimpleRouter()
router.register(r'subscription', SubscriptionViewSet, 'Subscription')
# router.register(r'accounts', AccountViewSet)
urlpatterns = router.urls

urlpatterns += [

  # url(r'^products/feed/$', ProductsFeedView.as_view(), name='products-feed'),
  # url(r'^delete-feed/(?P<pk>[0-9]+)/$', FavoriteFeeds.as_view(), name='delete-feed'),
]
