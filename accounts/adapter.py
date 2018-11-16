from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from accounts.custom_utils import CustomUtils

custom_utils = CustomUtils()


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # current_site = get_current_site(request)
        # activate_url = self.get_email_confirmation_url(
        #     request,
        #     emailconfirmation)

        activate_url = custom_utils.get_confirmation_url(emailconfirmation.key)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            # "current_site": current_site,
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
