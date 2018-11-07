"""EnCamp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^', include('shopification.urls')),
    url(r'^api/v1/', include('shopification.urls')),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^api/v1/user/', include('accounts.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^api/v1/core/', include('core.urls')),
    url(r'^api/v1/', include('subscription.urls')),
    url(r'social-login/$', views.social_login, name='social_login'),
    url(r'accounts/reset-password-form/(?P<uidb64>[-:\w]+)/(?P<token>[-:\w]+)/$',
        views.reset_password_form, name='reset_password_form'),
    url(r'^$', views.home, name='home')
]

try:
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
except:
    pass