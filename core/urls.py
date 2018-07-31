from django.conf.urls import url, include
from .views import *

# Registration URLs
urlpatterns = [

  url(r'^data/$',ListData.as_view(), name='list-data'),
  url(r'^feeds/$',ListRss.as_view(), name='list-rss'),
  url(r'^favorite/$',FavoriteFeeds.as_view(), name='favorite-feeds'),
  url(r'^trends/$',ListTrendingProduct.as_view(), name='trends'),
  url(r'^keywords/$',SimilarKeyword.as_view(), name='similar-keywords'),
  url(r'^list-influencer/', InfluencerList.as_view(), name='influencer-list'),
  url(r'^list-products/', CustomProductList.as_view(), name='product-list'),

]
