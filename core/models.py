from django.db import models
from accounts.models import User
from django.contrib.postgres.fields import JSONField
# Create your models here.


class RssFeed(models.Model):
    user = models.ForeignKey(User,
                             related_name='user_rss',
                             on_delete=models.CASCADE
                             )
    brand_name = models.CharField(max_length=255, null=False, blank=False)
    brand_url  = models.CharField(max_length=255, null=False, blank=False)
    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name

    class Meta:
        verbose_name = 'Feed'
        verbose_name_plural = 'Feeds'


class FavoriteSite(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='User',
                             on_delete=models.CASCADE
                             )
    feed = models.ForeignKey(RssFeed,
                              on_delete=models.CASCADE
                              )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feed.brand_name

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'


class StoreUrl(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(default='', max_length=255, blank=False, null=False)
    url = models.CharField(max_length=255, blank=False, null=False)
    revenue = models.CharField(max_length=255, blank=True, null=True)
    get_product = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"


class ProductDetail(models.Model):

    title = models.CharField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    img_link = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=5000, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class TrendingProduct(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Trending Product'
        verbose_name_plural = 'Trending Products'

    def __str__(self):
        return self.user.get_full_name()

