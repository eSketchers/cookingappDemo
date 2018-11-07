from django.conf.urls import url, include
from .views import *

from rest_framework import routers

# Registration URLs
# router = routers.SimpleRouter()
# router.register(r'subscription', SubscriptionViewSet, 'Subscription')

# urlpatterns = router.urls

urlpatterns = [
  url(r'shopify/$', ShopifyAuth.as_view(), name='shopify'),
  url(r'shopify/callback/$', finalize, name='shopify-callback'),
]
