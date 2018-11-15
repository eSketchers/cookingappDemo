from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_encode

from accounts.forms import SendResetEmailForm
from accounts.serializers import CustomUserCreateSerializer
from .models import User

from django.core.mail import send_mail


domain = "api.dropshipdynamo.com"
site_name = "Ecom Engine"


class UserAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'email',
        'is_admin',
        # 'account_actions',
    )
    readonly_fields = (
        'email',
        'is_admin',
        # 'account_actions',
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
            '<a class="button" href="{}">Send Reset Password Email</a>&nbsp;',
            reverse('admin:account-send-reset-email', args=[obj.pk]),
            # reverse('admin:account-send-reset-password-email', args=[obj.pk]),
        )

    account_actions.short_description = 'Account Actions'
    account_actions.allow_tags = True

    def process_email_password_reset(self, request, account_id, *args, **kwargs):
        return self.process_action(
            request=request,
            account_id=account_id,
            action_form=SendResetEmailForm,
            action_title='Admin Password Reset Email',
        )

    def process_action(
            self,
            request,
            account_id,
            action_form,
            action_title
    ):
        account = self.get_object(request, account_id)
        # if request.method != 'POST':
        #     form = action_form()
        # else:
        #     form = action_form(request.POST)

        domain_override = None,
        subject_template_name = 'registration/password_reset_subject.txt'
        email_template_name = 'registration/password_reset_email.html'
        use_https = False
        token_generator = default_token_generator
        from_email = settings.DEFAULT_FROM_EMAIL
        request = None
        html_email_template_name = None
        extra_email_context = None

        to_email = account.email

        context = {
            'email': to_email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(account.pk)).decode(),
            'user': account,
            'token': token_generator.make_token(account),
            'protocol': 'https',
        }
        prf = PasswordResetForm()
        prf.send_mail( subject_template_name=subject_template_name, email_template_name=email_template_name,
                                     context=context, from_email=from_email,
                to_email=to_email, html_email_template_name=html_email_template_name)

        url = reverse(
            'admin:auth_user_changelist'
            # 'admin:account_account_change',
            # args=[account.id],
            # current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name),
                       args=[self.id])

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

