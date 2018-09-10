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
    saved_feed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name

    class Meta:
        ordering = ['created_at', 'is_favorite','saved_feed']
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
    product_link = models.CharField(max_length=255, blank=True, null=True)
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


class CronStatus(models.Model):

    job_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_name


class Influencer(models.Model):

    name        = models.CharField(blank=True, null=True, max_length=255)
    username    = models.CharField(blank=True, null=True, max_length=255)
    url         = models.CharField(blank=True, null=True, max_length=255)
    type        = models.CharField(blank=True, null=True, max_length=255)
    count       = models.BigIntegerField(null=True, blank=True, default=0)
    profile_pic = models.CharField(blank=True, null=True, max_length=255)
    profile_pic_hd = models.CharField(blank=True, null=True, max_length=255)
    biograpghy      = models.CharField(blank=True, null=True, max_length=255)
    external_link  = models.CharField(blank=True, null=True, max_length=255)
    followed_by    = models.BigIntegerField(blank=True, null=True)
    follow         = models.BigIntegerField(blank=True, null=True)
    info           = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Influencer'
        verbose_name_plural = 'Influencers'

    def __str__(self):
        return self.type


class CustomProduct(models.Model):

    title = models.CharField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='images_product/%Y/%m/%d/', blank=True, null=True)
    video = models.FileField(upload_to='product_videos/%Y/%m/%d/', blank=True, null=True)
    ali_express = models.CharField(max_length=255, blank=True, null=True)
    product_link = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=5000, null=False, blank=False)
    actual_price = models.FloatField(default=0, null=True, blank=True)
    selling_price = models.FloatField(default=0, null=True, blank=True)
    profit = models.FloatField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Custom Product"
        verbose_name_plural = "Custom Products"


class FeedBack(models.Model):

    email = models.CharField(max_length=255 )
    feedback = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'feedback'
        verbose_name_plural = 'feedbacks'

    def __str__(self):
        return self.email


class Keyword(models.Model):

    key = models.CharField(max_length=255, blank=False, null=False)
    cpc = models.FloatField(max_length=65)
    volume = models.FloatField(max_length=65)
    region = models.CharField(max_length=45, blank=True, null=True)
    profitability = models.FloatField(max_length=255)
    product = models.ForeignKey('CustomProduct', related_name='hot_products', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'keyword'
        verbose_name_plural = 'keywords'

    def __str__(self):
        return self.key


class VideoGroup(models.Model):

    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Video Group'
        verbose_name_plural = 'Video Groups'

    def __str__(self):
        return self.name


class TrainingVideo(models.Model):

    url = models.CharField(max_length=255, blank=True, null=True)
    group = models.ForeignKey('VideoGroup', related_name='video_group', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.group.name


class BookmarkedProducts(models.Model):
    """ Model to save user bookmarked products
        and show in its saved items
    """
    title = models.CharField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    img_link = models.CharField(max_length=255, blank=True, null=True)
    product_link = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(default=0, null=True, blank=True)
    grams = models.CharField(max_length=255, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor

    class Meta:
        verbose_name = "Bookmarked Product"
        verbose_name_plural = "Bookmarked Products"


class FeedStore(models.Model):
    """Store user shopify url
    to get store products details.
    """
    brand_name = models.CharField(db_index=True, max_length=255, null=False, blank=False)
    brand_url = models.CharField(db_index=True, max_length=255, null=False, blank=False)
    user = models.ForeignKey(User,
                             related_name='user_feed',
                             on_delete=models.CASCADE
                             )
    feed = models.ForeignKey(RssFeed,
                              on_delete=models.CASCADE
                              )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name

    class Meta:
        ordering = ['created_at']
        verbose_name = 'User Feed Store'
        verbose_name_plural = 'User Feeds Stores.'


class FeedProducts(models.Model):
    """ Model to save user FeedStore model products
        and show products as a feeds.
    """
    title = models.CharField(db_index=True, max_length=255, blank=False, null=False)
    type = models.CharField(db_index=True, max_length=255, blank=True, null=True)
    vendor = models.CharField(db_index=True, max_length=255, blank=True, null=True)
    img_link = models.CharField(db_index=True, max_length=255, blank=True, null=True)
    product_link = models.CharField(db_index=True, max_length=255, blank=True, null=True)
    price = models.FloatField(default=0, null=True, blank=True)
    grams = models.CharField(max_length=255, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(FeedStore, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor

    class Meta:
        ordering = ['created_at']
        verbose_name = "Feedly Product"
        verbose_name_plural = "Feedly Products"
