from rest_framework import serializers
from .models import *


class FeedsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RssFeed
        fields = ('id', 'brand_name', 'brand_url', 'is_favorite',)


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteSite
        depth = 1
        fields = ('feed', )


class TrendingSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrendingProduct
        fields = ('data', )