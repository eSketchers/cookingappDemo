from rest_framework.views import APIView
from rest_framework import generics
from django.http import Http404
import requests
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
import boto3

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }
comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
# Create your views here.


class ListData(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        result = []
        variants = []
        product_details = {}
        url = request.data['link']
        page_res = self.get_page(url)
        if page_res['response']:
            for content in page_res['response']['feed']['entry']:
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
                    price = float(content['s:variant'][0]['s:price']['#text'])
                    unit = content['s:variant'][0]['s:price']['@currency']

                    product_details = {'published': content['published'],
                                       'grams': content['s:variant'][0]['s:grams'],
                                       'price': price,
                                       'unit': unit
                                       }

                else:
                    price = float(content['s:variant']['s:price']['#text'])
                    unit = content['s:variant']['s:price']['@currency']
                    product_details = { 'published': content['published'],
                                        'grams': content['s:variant']['s:grams'],
                                        'price': price,
                                        'unit': unit
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

            favorite = RssFeed.objects.filter(brand_name=page_res['response']['feed']['title'],
                                                    user=request.user).exists()
            if not favorite:
                RssFeed.objects.create(
                                    brand_name = page_res['response']['feed']['title'],
                                    brand_url = page_res['response']['feed']['id'].split("/collections")[0],
                                    user    = request.user
                                    )
            return Response(result, status=status.HTTP_200_OK)

        elif page_res['error']:
            if page_res['status_code'] == 430:
                return Response(page_res['error'], status=page_res['status_code'])
            else:
                return Response(page_res['error'], status=page_res['status_code'])
        else:
            url_error = "Response of url is not available."
            return Response(url_error, status=status.HTTP_404_NOT_FOUND)

    def get_page(self, link):
        payload = {}
        try:
            # req = urllib.request.Request(link)
            # with urllib.request.urlopen(req) as response:
            #     response = response.read()
            response = requests.get(link)
            if response.status_code == 200:
                res_dict = xmltodict.parse(response.text)
                payload.update({'response':res_dict})
                payload.update({'error': False})
                payload.update({'status_code': response.status_code})
                return payload
            elif response.status_code == 430:
                soup = BeautifulSoup(response.text, 'html.parser')
                txt = soup.findAll('p')
                payload.update({'response':False})
                payload.update({'error': txt[0].text})
                payload.update({'status_code': response.status_code})
                return payload
            else:
                payload.update({'response': False})
                payload.update({'error':response.text})
                payload.update({'status_code': response.status_code})
                return payload
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
            payload.update({'response': False})
            payload.update({'error': errh})
            payload.update({'status_code': response.status_code})
            return payload
        except requests.exceptions.ConnectionError as errc:
            payload.update({'response': False})
            payload.update({'error': errc})
            payload.update({'status_code': response.status_code})
            return payload
        except requests.exceptions.Timeout as errt:
            payload.update({'response': False})
            payload.update({'error': errt})
            payload.update({'status_code': response.status_code})
            return payload
        except requests.exceptions.RequestException as err:
            payload.update({'response': False})
            payload.update({'error': err})
            payload.update({'status_code': response.status_code})
            return payload


class ListRss(APIView):
    """
       List all searched urls of specific user.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        feeds = RssFeed.objects.filter(user=request.user)
        serializer = FeedsSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    def get_object(self, pk):
        try:
            return FavoriteSite.objects.get(feed_id=pk, user=self.request.user)
        except RssFeed.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        favorite = self.get_object(pk)
        favorite.delete()
        RssFeed.objects.filter(pk=pk).update(is_favorite=False)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        longest = 0

        client = RestClient(email,password)

        try:
            key_phrase = comprehend.detect_key_phrases(Text=self.request.data['keyword'], LanguageCode='en')
            len_result = len(key_phrase['KeyPhrases'])
            if  len_result > 0:
                for key in key_phrase['KeyPhrases']:
                    if len(key['Text']) > longest:
                        s_keyword = key['Text']
                        longest = len(key['Text'])
            else:
                s_keyword = self.request.data['keyword']
        except Exception as e:
            s_keyword = self.request.data['keyword']


        post_data = dict()
        post_data["1"] = dict(
            keyword= s_keyword,
            country_code="US",
            language="en",
            limit=50,
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



