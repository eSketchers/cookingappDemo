from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
import time
from allauth.account.models import EmailAddress

USER = settings.AUTH_USER_MODEL


def file_upload_to(instance, filename):
    try:
        filename = '/'.join([instance.__class__.__name__, str(timezone.now().strftime('%Y/%m/%d')),
                  str(int(time.time())) + '_' + filename])
    except Exception as e:
        filename = str(int(time.time()))
    return filename


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        try:
            user = User.objects.get(email=email)
        except Exception as ex:
            user = self.model(
                email=self.normalize_email(email),
                last_login=timezone.now(),
                **extra_fields
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):

        user = self.create_user(email, password=password, **extra_fields)
        user.is_admin = True
        user.is_active = True
        user.is_verified = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        # Now add this user's email address to EmailAddress table
        # Otherwise, user won't be able to login.
        email_address = EmailAddress()
        email_address.user = user
        email_address.verified = True
        email_address.primary = True
        email_address.email = email
        email_address.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address_1 = models.TextField(null=True, blank=True)
    address_2 = models.TextField(null=True, blank=True)
    post_code = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    picture = models.ImageField(upload_to=file_upload_to, null=True, blank=True, max_length=5000)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = u"User"
        verbose_name_plural = u"Users"

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name+' '+self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class MobileVerificationCode(models.Model):
    """
    Model for storing mobile verification codes for password reset
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='mobile_verification_code')
    code = models.TextField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)