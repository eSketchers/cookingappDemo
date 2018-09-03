from .models import User
import allauth.account.admin
from allauth.account.models import EmailAddress

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import os, hashlib
from accounts.serializers import CustomUserCreateSerializer


class UserAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('is_admin','is_superuser','is_active','user_permissions','groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def save_model(self, request, obj, form, change):
        data = dict(email=obj.email)
        user = User.objects.filter(email=data['email'])
        if user.exists() is False:
            obj.save()
            serializer = CustomUserCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            email_address = EmailAddress()
            email_address.user = user[0]
            email_address.verified = True
            email_address.primary = True
            email_address.email = data['email']
            email_address.save()
        else:
            obj.save()

admin.site.register(User, UserAdmin)

