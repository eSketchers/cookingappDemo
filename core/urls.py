from django.conf.urls import url, include
from .views import *

# Registration URLs
urlpatterns = [

  url(r'^data/$',ListData.as_view(), name='list-data'),
  url(r'^feeds/$',ListRss.as_view(), name='list-rss'),
  url(r'^delete-feed/(?P<pk>[0-9]+)/$', FavoriteFeeds.as_view(), name='delete-feed'),
  url(r'^favorite/$',FavoriteFeeds.as_view(), name='favorite-feeds'),
  url(r'^trends/$',ListTrendingProduct.as_view(), name='trends'),
  url(r'^keywords/$',SimilarKeyword.as_view(), name='similar-keywords'),
  url(r'^list-influencer/', InfluencerList.as_view(), name='influencer-list'),
  url(r'^list-products/', CustomProductList.as_view(), name='product-list'),
  url(r'^feedback/', FeedBackView.as_view(), name='feedback'),
  url(r'^category-list/', InfluencerCategory.as_view(), name='category'),
  url(r'^keywords-product/', KeywordProductView.as_view(), name='keyword-product'),
  url(r'^list-group/', VideoGroupView.as_view(), name='list-group'),
  url(r'^list-videos/', TrainingVideoView.as_view(), name='list-videos'),
  url(r'^save-item/', BookmarkProductsView.as_view(), name='save-items'),
  url(r'^click_create/', ClickFunnelUserCreate.as_view(), name='create-user-click'),
  url(r'^rm-item/(?P<pk>[0-9]+)/$', BookmarkProductsView.as_view(), name='delete-items'),
  url(r'^feedstore/$', FeedlyView.as_view(), name='feed-stores'),
  url(r'^feedstore/d/(?P<pk>[0-9]+)/$', FeedlyView.as_view(), name='remove-feeds'),
  url(r'^products/feed/$', ProductsFeedView.as_view(), name='products-feed'),

]
