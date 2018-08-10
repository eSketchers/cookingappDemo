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
    search_fields = ('title',)


class FeedBackAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at',]
    search_fields = ('email',)


class KeywordAdmin(admin.ModelAdmin):
    list_display = ['key', 'cpc', 'volume', 'region',
                    'actual_price','store_price',
                    'profit', 'conversion_rate']
    exclude = ('profitability',)
    search_fields = ('key',)

    def save_model(self, request, obj, form, change):
        profitability = obj.store_price * (obj.profit/100) * obj.cpc
        obj.profitability = profitability
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(RssFeed)
admin.site.register(FavoriteSite)
admin.site.register(StoreUrl, StoreAdmin)
admin.site.register(ProductDetail, ProductAdmin)
admin.site.register(TrendingProduct)
admin.site.register(Influencer, InfluencerAdmin)
admin.site.register(CustomProduct, CustomProductAdmin)
admin.site.register(FeedBack, FeedBackAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(CronStatus)