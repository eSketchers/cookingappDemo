from django.contrib import admin
from core.models import *


# class MyModelAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         models.TextField: {'widget': RichTextEditorWidget},
#     }

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'type']
    search_fields = ('title',)


class StoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'revenue', 'get_product']


class InfluencerAdmin(admin.ModelAdmin):
    list_display = ['type', 'url', 'name']
    search_fields = ('url','name')


class CustomProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'user']
    search_fields = ('title','user')


class FeedBackAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at',]
    search_fields = ('email',)

# Register your models here.
admin.site.register(RssFeed)
admin.site.register(FavoriteSite)
admin.site.register(StoreUrl, StoreAdmin)
admin.site.register(ProductDetail, ProductAdmin)
admin.site.register(TrendingProduct)
admin.site.register(Influencer, InfluencerAdmin)
admin.site.register(CustomProduct, CustomProductAdmin)
admin.site.register(FeedBack, FeedBackAdmin)
admin.site.register(CronStatus)