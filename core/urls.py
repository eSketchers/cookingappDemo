from django.conf.urls import url, include
from .views import *

# Registration URLs
urlpatterns = [

  url(r'^data/$',ListData.as_view(), name='list-data'),
  url(r'^feeds/$',ListRss.as_view(), name='list-rss'),
  url(r'^favorite/$',FavoriteFeeds.as_view(), name='favorite-feeds'),

]
