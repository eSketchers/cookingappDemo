from rest_auth.registration.serializers import VerifyEmailSerializer
from rest_auth.registration.views import APIView, ConfirmEmailView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from django.shortcuts import render
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from accounts.serializers import CustomUserDetailsSerializer, SerializeUserDetails
from django.contrib.auth import get_user_model
from accounts.custom_utils import IMAGE_EXT

# Get the UserModel
User = get_user_model()


class CustomVerifyEmailView(APIView, ConfirmEmailView):
    """
    Confirm user email from its access token after sign-up.
    :param APIView: Inherit django api view.
    :param ConfirmEmailView: Inherit allauth package ConfirmEmailView.
    :param key: kwargs['key'] token send in email on sign up.
    :return success message:

    """

    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'result': 'Email address has been successfully verified.'}, status=status.HTTP_200_OK)


class FacebookLoginView(SocialLoginView):
    """
    View for providing social login using Facebook OAuth2.

    :param SocialLoginView: Inherit socialLoginView
                            class from django allauth.
    :return instance: User instance.
    """
    adapter_class = FacebookOAuth2Adapter


class GoogleLoginView(SocialLoginView):
    """
    View for providing social login using google OAuth2.

    :param SocialLoginView: Inherit socialLoginView
                            class from django allauth.
    :return instance: User instance.
    """
    adapter_class = GoogleOAuth2Adapter


class EditUserApiView(APIView):
    """

    Update user detail partially
    :param APIView: Inherit django APIView.
    :return response: serialize data as a response.

    """
    permission_classes = (IsAuthenticated,)
    allowed_methods = ('POST', 'PUT')

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user_instance = self.get_object()
        serializer = CustomUserDetailsSerializer(user_instance, data=request.data, context={'request':request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageUploadView(APIView):

    """Api Endpoint to upload user image.

    :param APIView: Inherit django bass api view.
    :param image: Contains file as a image.
    :return instance: User detail instance.

    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    allowed_methods = ('POST',)

    def get_object(self):
        return self.request.user

    def post(self, request, format=None):
        user_instance = self.get_object()
        obj = request.FILES.get('image', None)
        if obj is None:
            raise ParseError("No Image selected.")
        if not obj.content_type in IMAGE_EXT:
            raise ParseError("Not a valid Image Extension.")
        user_instance.picture.delete(False)
        user_instance.picture.save(obj.name, obj, save=True)
        serializer = SerializeUserDetails(instance=user_instance, context={'request':request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def social_login(request):
    return render(request,'account/social_login.html')


def reset_password_form(request, uidb64, token):
    context = {
        'uid': uidb64,
        'token': token
    }
    return render(request,'account/password_reset_form.html', context=context)


def home(request):
    return render(request, 'home.html')