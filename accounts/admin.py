from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_encode

from accounts.serializers import CustomUserCreateSerializer
from .models import User

domain = "api.dropshipdynamo.com"
site_name = "Ecom Engine"


class UserAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'email',
        'is_admin',
        'account_actions',
    )
    readonly_fields = (
        'account_actions',
    )
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth')}),
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<account_id>.+)/send-reset-password-email/$',
                self.admin_site.admin_view(self.process_email_password_reset),
                name='account-send-reset-email',
            ),
        ]
        return custom_urls + urls

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Reset Password</a>&nbsp;',
            reverse('admin:account-send-reset-email', args=[obj.pk]),
        )

    account_actions.short_description = 'Account Actions'
    account_actions.allow_tags = True

    def process_email_password_reset(self, request, account_id, *args, **kwargs):
        try:
            return self.process_action(
                request=request,
                account_id=account_id,
            )
        except Exception as e:
            account = self.get_object(request, account_id)
            messages.error(request, 'Could not send email to {}'.format(account.email))
            return HttpResponseRedirect(reverse('admin:accounts_user_changelist'))

    def process_action(self, request, account_id):
        account = self.get_object(request, account_id)

        subject_template_name = 'admin/account/email/password_reset_subject.txt'
        email_template_name = 'admin/account/email/password_reset.html'
        token_generator = default_token_generator
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = account.email  # use list or tuple
        site = get_current_site(request)

        context = {
            'email': to_email,
            'domain': site.domain,
            'site_name': site.name,
            'uid': urlsafe_base64_encode(force_bytes(account.pk)).decode(),
            'user': account,
            'token': token_generator.make_token(account),
            'protocol': 'https',
        }

        subject = loader.render_to_string(subject_template_name)
        subject = "".join(subject.splitlines())  # remove superfluous line breaks
        message = loader.render_to_string(email_template_name, context)
        msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
        msg.attach_alternative(message, "text/html")
        msg.send()

        messages.success(request, 'Reset password email sent to {}'.format(to_email))

        return HttpResponseRedirect(reverse('admin:accounts_user_changelist'))

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

