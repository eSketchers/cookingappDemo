from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from rest_auth.serializers import (UserDetailsSerializer,
                                   PasswordResetSerializer,
                                    PasswordResetConfirmSerializer)
from .forms import CustomPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import ValidationError

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

from rest_framework import serializers
from datetime import datetime, timezone


# Get the UserModel
UserModel = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = UserModel
        fields = ('id', 'email', 'first_name', 'last_name', 'date_of_birth',
                  'address_1', 'address_2', 'picture', 'telephone', 'post_code')
        read_only_fields = ('email',)

class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        max_length=255,
        required= False
    )
    last_name = serializers.CharField(
        max_length=255,
        required=False
    )
    date_of_birth = serializers.DateField(
        required=False
    )
    address_1 = serializers.CharField(
        required=False
    )
    address_2 = serializers.CharField(
        required=False
    )
    post_code = serializers.CharField(
        max_length=255,
        required=False
    )
    telephone = serializers.CharField(
        max_length=20,
        required=False
    )
    picture = serializers.ImageField(
        required=False,
        max_length=5000
    )



    # def validate_username(self, username):
    #     username = get_adapter().clean_username(username)
    #     return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        """
        Save extra fields or other information like files using this method
        :param request:
        :param user: User to be saved
        :return:
        """
        if request.FILES and request.FILES['picture']:
            self.save_profile_picture(user, request.FILES['picture'])

        if self.cleaned_data.get('date_of_birth'):
            user.date_of_birth = self.cleaned_data.get('date_of_birth')

        if self.cleaned_data.get('address_1'):
            user.address_1 = self.cleaned_data.get('address_1')

        if self.cleaned_data.get('address_2'):
            user.address_2 = self.cleaned_data.get('address_2')

        if self.cleaned_data.get('post_code'):
            user.post_code = self.cleaned_data.get('post_code')

        if self.cleaned_data.get('telephone'):
            user.telephone = self.cleaned_data.get('telephone')

        user.save()

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', None),
            'last_name': self.validated_data.get('last_name', None),
            'date_of_birth': self.validated_data.get('date_of_birth', None),
            'address_1': self.validated_data.get('address_1', None),
            'address_2': self.validated_data.get('address_2', None),
            'post_code': self.validated_data.get('post_code', None),
            'telephone': self.validated_data.get('telephone', None),
            'picture': self.validated_data.get('picture', None),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        email = setup_user_email(request, user, [])
        return user

    def save_profile_picture(self, user, picture):
        user.picture = picture
        user.save()
        # with open('test','wb+') as destination:
        #     for chunk in picture.chunks():
        #         destination.write(chunk)


class CustomPasswordResetSerializer(PasswordResetSerializer):

    password_reset_form_class = CustomPasswordResetForm

    def get_email_options(self):
        return {
            'subject_template_name': 'account/email/password_reset_key_subject.txt',
            'email_template_name': 'account/email/password_reset_key_message.txt',
            'html_email_template_name': 'account/email/password_reset_key_message.html',
            'extra_email_context': {}
        }


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    """
    Serializer for requesting a password reset using web or mobile app
    If a user resets password from web app, the frontend must provide
    uid and token. If a user resets password from mobile app, email address
    of the user must be provided.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField(required=False)
    token = serializers.CharField(required=False)
    code = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=False)

    set_password_form_class = SetPasswordForm

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        if 'uid' in attrs:
            try:
                uid = force_text(uid_decoder(attrs['uid']))
                self.user = UserModel._default_manager.get(pk=uid)
            except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
                raise ValidationError({'uid': ['Invalid value']})

        # If resetting password from mobile app
        elif getattr(settings, 'USE_MOBILE_VERIFICATION', False) and 'email' in attrs:
            try:
                self.user = UserModel._default_manager.get(email=attrs['email'])
                try:
                    if self.user.mobile_verification_code.code == attrs['code']:
                        # Check if verification code has not expired, default is 3 days
                        days = getattr(settings, 'PASSWORD_RESET_TIMEOUT_DAYS', 3)
                        delta = datetime.now(tz=timezone.utc) - self.user.mobile_verification_code.created_at
                        if delta.days >= days:
                            raise ValidationError({'code': ['This code has expired, please request a '
                                                            'new verification code.']})


                    else:
                        raise ValidationError({'code': ['Invalid value']})
                except ValidationError as e:
                    raise e
                except:
                    raise ValidationError({'code': ['Invalid value']})
            except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
                raise ValidationError({'email': ['Invalid value']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if 'uid' in attrs and not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        result = self.set_password_form.save()
        # Now delete the code from db
        try:
            self.user.mobile_verification_code.delete()
        except:
            pass
        return result