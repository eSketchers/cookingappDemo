from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import random
from accounts.models import MobileVerificationCode
from django import forms


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
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override

            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            # Check if mobile verification code setting is enabled in settings.py
            use_mobile_verification_code = getattr(settings, 'USE_MOBILE_VERIFICATION', False)
            if use_mobile_verification_code:
                mobile_verification_code = self.generate_verification_code_for_user(user)
                context['mobile_verification_code'] = mobile_verification_code
                context['use_mobile_verification_code'] = True  # Render verification part in template
            else:
                context['use_mobile_verification_code'] = False  # Do not render

            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )

            # Now save the mobile verification code in DB
            if use_mobile_verification_code:
                code = MobileVerificationCode(user=user, code=mobile_verification_code)
                code.save()

    def generate_verification_code_for_user(self, user):
        """
        Generates a verification code for user for password reseting using mobile
        :param user:
        :return: Verification code
        """
        code_length = 5
        try:
            code_length = settings.PASSWORD_RESET_VERIFICATION_CODE_LENGTH
        except:
            pass

        code = random.randint(pow(10,code_length-1),pow(10,code_length)-1)

        return code
