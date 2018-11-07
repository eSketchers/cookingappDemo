# Create your views here.
import uuid

import shopify
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)


class ShopifyAuth(RedirectView):
    # query_string = True

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        state = str(uuid.uuid1())
        scope = 'write_products'
        scopes = ['write_products']
        forwardingAddress = 'https://798392c1.ngrok.io'
        redirectUri = forwardingAddress + '/shopify/callback'
        shop = self.request.GET.get('shop')
        installUrl = None


        if shop:
            # session = shopify.Session("SHOP_NAME.myshopify.com")
            session = shopify.Session(shop)
            permission_url = session.create_permission_url(scopes, redirectUri, state)
            installUrl = permission_url
            # installUrl = 'https://' + shop + '/admin/oauth/authorize?client_id=' + settings.SHOPIFY_API_KEY + '&scope=' + scope + '&state=' + state + '&redirect_uri=' + redirectUri;
            return installUrl


# class ShopifyCallback(TemplateView):
#     template_name = 'shopification/home.html'

# def get_context_data(self, **kwargs):
def finalize(request):
    shop_url = request.GET.get('shop')

    session = shopify.Session(shop_url)
    token = session.request_token(request.GET)

    print(request.GET)
    request.session['shopify'] = {
        "shop_url": shop_url,
        "access_token": token
    }

    return HttpResponse(token)
