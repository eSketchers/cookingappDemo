from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import random
from accounts.models import MobileVerificationCode
from django import forms

domain = "api.dropshipdynamo.com"
site_name = "Ecom Engine"


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom Password Reset Form, which for generating 6 digit verification code
    for mobile applications
    """
    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            # if not domain_override:
            #     current_site = get_current_site(request)
            #     site_name = current_site.name
            #     domain = current_site.domain
            # else:
            #     site_name = domain = domain_override


            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )


class PasswordSetForm(PasswordResetForm):
    """
    Custom Password Reset Form, which for generating 6 digit verification code
    for mobile applications
    """
    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            # if not domain_override:
            #     current_site = get_current_site(request)
            #     site_name = current_site.name
            #     domain = current_site.domain
            # else:
            #     site_name = domain = domain_override

            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )


class UserActionForm(forms.Form):
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )
    send_email = forms.BooleanField(
        required=False,
    )

    @property
    def email_subject_template(self):
        return 'email/account/notification_subject.txt'

    @property
    def email_body_template(self):
        raise NotImplementedError()

    def form_action(self, account, user):
        raise NotImplementedError()

    def save(self, account, user):
        try:
            account, action = self.form_action(account, user)
        # except errors.Error as e:
        except Exception as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise
        if self.cleaned_data.get('send_email', False):
            send_mail(
                subject=self.email_subject_template,
                message=self.email_body_template,
                from_email= settings.DEFAULT_FROM_EMAIL,
                recipient_list=[account.user.email],
                # context = {
                #     "account": account,
                #     "action": action,
                #     'email': account.user.email,
                #     'domain': domain,
                #     'site_name': site_name,
                #     'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                #     'user': user,
                #     'token': token_generator.make_token(user),
                #     'protocol': 'https' if use_https else 'http',
                # }
            )
        return account, action


class SendResetEmailForm(UserActionForm):
    # amount = forms.IntegerField(
    #     min_value=Account.MIN_WITHDRAW,
    #     max_value=Account.MAX_WITHDRAW,
    #     required=True,
    #     help_text='How much to withdraw?',
    # )
    email_body_template = 'email/account/withdraw.txt'
    field_order = (
        # 'amount',
        # 'comment',
        # 'send_email',
    )

    def save(self, account, user):
        subject_template_name = 'registration/password_reset_subject.txt',
        email_template_name = 'registration/password_reset_email.html',
        token_generator = default_token_generator
        html_email_template_name = None
        email = account.email

        context = {
            'email': email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(account.pk)).decode(),
            'user': account,
            'token': token_generator.make_token(user),
            'protocol': 'https',
        }
        PasswordResetForm.send_mail(
            subject_template_name, email_template_name, context, settings.DEFAULT_FROM_EMAIL,
            email, html_email_template_name=html_email_template_name,
        )
