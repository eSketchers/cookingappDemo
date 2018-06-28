from rest_framework import serializers
from .models import *


class FeedsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RssFeeds
        fields = ('id', 'brand_name', 'brand_url', 'is_favorite',)


class FavoritesSerializer(serializers.ModelSerializer):
    # feeds = FeedsSerializer()

    class Meta:
        model = FavoriteSites
        depth = 1
        fields = ('feeds', )