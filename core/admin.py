from django.contrib import admin
from core.models import *


# class MyModelAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         models.TextField: {'widget': RichTextEditorWidget},
#     }

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'type']


class StoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'revenue', 'get_product']


# Register your models here.
admin.site.register(RssFeed)
admin.site.register(FavoriteSite)
admin.site.register(StoreUrl, StoreAdmin)
admin.site.register(ProductDetail, ProductAdmin)