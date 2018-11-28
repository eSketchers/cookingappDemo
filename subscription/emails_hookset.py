import hashlib
import random

from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings


class DefaultHookSet(object):

    def trail_end_email(self, to, ctx):
        subject = render_to_string("subscription/email/trail_end.txt", ctx)
        subject = "".join(subject.splitlines())  # remove superfluous line breaks
        message = render_to_string("subscription/email/trail_end.html", ctx)
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, to)
        msg.attach_alternative(message, "text/html")
        msg.send()

hookset = DefaultHookSet()
