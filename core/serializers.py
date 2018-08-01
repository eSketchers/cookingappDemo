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
        fields = ('id','feed', )


class TrendingSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrendingProduct
        fields = ('data', )


class InfluencerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Influencer
        fields = ('url','type','count','name','username',
                  'profile_pic_hd','biograpghy','external_link',
                  'followed_by','follow',)


class CustomProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomProduct
        fields = ('title','type','vendor','image','description',
                  'product_link','ali_express',)