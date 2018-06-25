from rest_framework_jwt.views import refresh_jwt_token
from django.conf.urls import url, include
from django.views.generic import TemplateView

from . import views

from rest_auth.views import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView,
)

from rest_auth.registration.views import RegisterView, VerifyEmailView
from .views import ListData

# Registration URLs
urlpatterns = [

  url(r'^data/$',ListData.as_view(), name='list-data'),

]
