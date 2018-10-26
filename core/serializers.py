from rest_framework import serializers
from .models import *


class FeedsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RssFeed
        fields = ('id', 'brand_name', 'brand_url', 'is_favorite','saved_feed')


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
    save_item = serializers.SerializerMethodField()

    class Meta:
        model = CustomProduct
        fields = ('id', 'title','type','vendor','image','video','description',
                  'product_link','ali_express','actual_price',
                  'selling_price','profit', 'released_date', 'save_item',)

    def get_save_item(self, obj):
        # return BookmarkedProducts.objects.filter(user=self.context['request'].user, title=obj.title).exists()
        return SavedLookupProduct.objects.filter(user=self.context['request'].user,
                                          product_type='hot', product_id=obj.id).exists()

class KeywordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Keyword
        fields = ('key', 'cpc', 'volume', 'region',
                  'profitability')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Influencer
        fields = ('type',)


class VideoGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoGroup
        fields = ('name',)


class TrainingVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingVideo
        depth = 1
        fields = ('id','title', 'embed', 'thumbnail', 'group','created_at')


class BookmarkProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookmarkedProducts
        fields = ('id','title','type','vendor','img_link','price',
                  'unit','grams','published_at','product_link',
                  'description','created_at',)


class SavedLookupSerializer(serializers.ModelSerializer):

    class Meta:
        model = SavedLookupProduct
        depth = 1
        fields = '__all__'


class FeedStoreSerializer(serializers.ModelSerializer):
    """Serializer to serialize and
       save store to get its products
       feeds.
    """

    class Meta:
        model = FeedStore
        depth = 1
        fields = ('id','feed','user','brand_name',
                  'brand_url','feed', )


class ProductFeedSerializer(serializers.ModelSerializer):
    save_item = serializers.SerializerMethodField()

    class Meta:
        model = FeedProducts
        fields = ('id', 'title','type','vendor','img_link','description',
                  'product_link','published_at','price',
                  'unit','grams','created_at', 'save_item',)

    def get_save_item(self, obj):
        # return BookmarkedProducts.objects.filter(user=self.context['request'].user, title=obj.title).exists()
        return SavedLookupProduct.objects.filter(user=self.context['request'].user,
                                                 product_type='feed', product_id=obj.id).exists()