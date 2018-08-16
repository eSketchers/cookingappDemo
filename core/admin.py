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
    list_display = ['title', 'type',]
    exclude = ('profit',)
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        profit_margin = (obj.selling_price - obj.actual_price)
        obj.profit = profit_margin
        obj.save()


class FeedBackAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at',]
    search_fields = ('email',)


class KeywordAdmin(admin.ModelAdmin):
    list_display = ['key', 'cpc', 'volume', 'region',]
    exclude = ('profitability','profit',)
    search_fields = ('key',)

    def save_model(self, request, obj, form, change):
        conv_rate = 0.01
        markup = (obj.product.selling_price - obj.product.actual_price)
        margin = (markup / obj.product.actual_price) * 100
        profitability = obj.product.selling_price * margin/100 * conv_rate
        obj.profitability = profitability
        obj.save()


class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at' ]
    search_fields = ('name',)


class TrainingVideoAdmin(admin.ModelAdmin):
    list_display = ['group','is_active','created_at']
    search_fields = ('group',)


# Register your models here.
admin.site.register(RssFeed)
admin.site.register(FavoriteSite)
admin.site.register(CronStatus)
admin.site.register(TrendingProduct)
admin.site.register(StoreUrl, StoreAdmin)
admin.site.register(ProductDetail, ProductAdmin)
admin.site.register(Influencer, InfluencerAdmin)
admin.site.register(CustomProduct, CustomProductAdmin)
admin.site.register(FeedBack, FeedBackAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(VideoGroup, GroupAdmin)
admin.site.register(TrainingVideo, TrainingVideoAdmin)
