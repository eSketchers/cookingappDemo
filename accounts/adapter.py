from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from accounts.custom_utils import CustomUtils

custom_utils = CustomUtils()


class CustomAccountAdapter(DefaultAccountAdapter):
    """ Inherit Default account adapter of django
        allauth to customize email service.
    """
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = custom_utils.get_confirmation_url(emailconfirmation.key)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "key": emailconfirmation.key,
            "title": "Welcome",
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)
