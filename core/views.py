from rest_framework.views import APIView
from rest_framework import generics
from django.http import Http404
import urllib.request
import xmltodict
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from core.client import RestClient
from core.pagination import LargeResultsSetPagination
from rest_framework.filters import SearchFilter

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }
# Create your views here.


class ListData(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        result = []
        variants = []
        product_details = {}
        url = request.data['link']
        page_res = self.get_page(url)
        if page_res:
            for content in page_res['feed']['entry']:
                soup = BeautifulSoup(content['summary']['#text'], 'html.parser')
                src = soup.find_all("img")[0].attrs['src']
                tb_data = soup.find('table').find_all('tr')[1].find('td')
                p_tag = tb_data.find_all("p", limit=2)
                if len(p_tag) == 2:
                    para_tag = str(p_tag[0]) + str(p_tag[1])
                elif len(p_tag) == 1:
                    para_tag = str(p_tag[0])
                else:
                    para_tag = tb_data.get_text()
                if isinstance(content['s:variant'], list):
                    variants = []
                    variants.append(content['s:variant'])
                else:
                    product_details = { 'published': content['published'], 'grams': content['s:variant']['s:grams'],
                                  'price': content['s:variant']['s:price']['@currency'] + ' ' + content['s:variant']['s:price']['#text']
                                }
                data = {
                    'img_src' : src,
                    'product_link':content['link']['@href'],
                    'product_keyword':content['link']['@href'].split('/')[-1],
                    'details' : para_tag,
                    'title': content['title'],
                    'vendor'  : content['s:vendor'],
                    'type'    : content['s:type'],
                    's_variants': product_details,
                    'mul_variants': variants
                }
                result.append(data)

            favorite = RssFeed.objects.filter(brand_name=page_res['feed']['title'],
                                                    user=request.user).exists()
            if not favorite:
                RssFeed.objects.create(
                                    brand_name = page_res['feed']['title'],
                                    brand_url = page_res['feed']['id'].split("/collections")[0],
                                    user    = request.user
                                    )
            return Response(result, status=status.HTTP_200_OK)
        else:
            url_error = True
            return Response(url_error, status=status.HTTP_404_NOT_FOUND)

    def get_page(self, link):
        error = False
        try:
            req = urllib.request.Request(link)
            with urllib.request.urlopen(req) as response:
                response = response.read()
            res_dict = xmltodict.parse(response)
            return res_dict
        except Exception as e:
            return


class ListRss(APIView):
    """
       List all searched urls of specific user.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        feeds = RssFeed.objects.filter(user=request.user)
        serializer = FeedsSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            return RssFeed.objects.get(pk=pk)
        except RssFeed.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        feed = self.get_object(pk)
        feed.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteFeeds(APIView):
    """
       List all favorite feeds.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        feeds = FavoriteSite.objects.filter(user=request.user)
        serializer = FavoritesSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        response = {}
        try:
            FavoriteSite.objects.create(user=request.user,
                                         feed_id = request.data['id']
                                         )
            RssFeed.objects.filter(id=request.data['id']).update(is_favorite=True)
            response.update({'success':True})
            status_code = status.HTTP_201_CREATED
        except Exception as e:
            response.update({'success': False})
            status_code = status.HTTP_403_FORBIDDEN

        return Response(response, status=status_code)


class ListTrendingProduct(APIView):
    """ List all trending products feeds.
        """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        trending = TrendingProduct.objects.filter(user=request.user)
        serializer = TrendingSerializer(trending, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SimilarKeyword(APIView):

    def post(self, *args, **kwargs):

        email = "henrywilliam2020@gmail.com"
        password = "a6B7Ftr5K4uWjxkl"

        client = RestClient(email,password)
        s_keyword = self.request.data['keyword']

        post_data = dict()
        post_data["1"] = dict(
            keyword= s_keyword,
            country_code="US",
            language="en",
            limit=5,
            offset=0,
            orderby="search_volume,desc",
            filters=[
                ["cpc", ">", 0],
                "or",
                [
                    ["search_volume", ">", 0],
                    "and",
                    ["search_volume", "<=", 1000]
                ],
                "and",
                [
                    "search_volume", "in", [10, 500]
                ]
            ]
        )

        response = client.post("/v2/kwrd_finder_similar_keywords_get", dict(data=post_data))
        if response["status"] == "error":
            print("error. Code: %d Message: %s" % (response["error"]["code"], response["error"]["message"]))
            return Response(response["error"]["message"], status=response["error"]["code"])
        else:
            return Response(response["results"]['1'], status=status.HTTP_200_OK)


class InfluencerList(generics.ListAPIView):

    serializer_class = InfluencerSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('^username', 'type')

    def get_queryset(self):
        queryset = Influencer.objects.filter(info=True).order_by('created_at')
        return queryset


class CustomProductList(generics.ListAPIView):

    serializer_class = CustomProductSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = CustomProduct.objects.all().order_by('created_at')
        return queryset
