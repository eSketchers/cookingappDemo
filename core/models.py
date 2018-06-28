from django.db import models
from accounts.models import User
# Create your models here.


class RssFeeds(models.Model):
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


class FavoriteSites(models.Model):
    user = models.ForeignKey(User,
                             related_name='user',
                             verbose_name='User',
                             on_delete=models.CASCADE
                             )
    feeds = models.ForeignKey(RssFeeds,
                              related_name='feeds',
                              on_delete=models.CASCADE
                              )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feeds.brand_name

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'