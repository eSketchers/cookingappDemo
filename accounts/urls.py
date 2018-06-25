from rest_framework_jwt.views import refresh_jwt_token
from django.conf.urls import url, include
from django.views.generic import TemplateView

from . import views

from rest_auth.views import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView,
)

from rest_auth.registration.views import RegisterView, VerifyEmailView


# Registration URLs
urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='rest_register'),
    url(r'^verify-email/$', VerifyEmailView.as_view(), name='rest_verify_email'),
    url(r'^account-confirm-email/(?P<key>[-:\w]+)/$',
        views.CustomVerifyEmailView.as_view(), name='account_confirm_email'),

]

# Authorization and account management urls
urlpatterns += [
    url(r'^refresh-token/', refresh_jwt_token),
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='rest_password_reset'),
    url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    url(r'^login/$', LoginView.as_view(), name='rest_login'),
    url(r'^login/facebook/$', views.FacebookLoginView.as_view(), name='fb_login'),
    url(r'^login/google/$', views.GoogleLoginView.as_view(), name='google_login'),
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^password/change/$', PasswordChangeView.as_view(),
        name='rest_password_change'),
    url(r'^$', UserDetailsView.as_view(), name='rest_user_details'),
]
