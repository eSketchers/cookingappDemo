from django.db.models import F
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
import os, hashlib
from accounts.models import EmailAddress
from accounts.serializers import CustomUserCreateSerializer
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }
comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
# Create your views here.


class ListData(APIView):
    """Get Xml of input store and
       list its products feeds into feeds component.
    """
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
                qs = BookmarkedProducts.objects.filter(user=request.user, title=content['title']).exists()
                data = {
                    'img_src' : src,
                    'product_link':content['link']['@href'],
                    'product_keyword':content['link']['@href'].split('/')[-1],
                    'details' : para_tag,
                    'title': content['title'],
                    'vendor'  : content['s:vendor'],
                    'type'    : content['s:type'],
                    's_variants': product_details,
                    'mul_variants': variants,
                    'save_item': qs
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
            elif page_res['status_code'] == 404:
                error = "Store url is invalid."
                return Response(error, status=page_res['status_code'])
            elif page_res['status_code'] == 503:
                error = "Store is currently down or having some other issues. Try later"
                return Response(error, status=page_res['status_code'])
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
            payload.update({'status_code': status.HTTP_503_SERVICE_UNAVAILABLE})
            return payload
        except requests.exceptions.Timeout as errt:
            payload.update({'response': False})
            payload.update({'error': errt})
            payload.update({'status_code': status.HTTP_408_REQUEST_TIMEOUT})
            return payload
        except requests.exceptions.RequestException as err:
            payload.update({'response': False})
            payload.update({'error': err})
            payload.update({'status_code': status.HTTP_404_NOT_FOUND})
            return payload


class ListRss(APIView):
    """ Show all searched urls of specific user,
        in his Stores component.
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
    search_fields = ('^username',)
    queryset = Influencer.objects.filter(info=True).order_by('-created_at')

    def get_queryset(self):
        min_range = self.request.query_params.get('min_range',None)
        max_range = self.request.query_params.get('max_range',None)
        category = self.request.query_params.get('category',None)

        if min_range and max_range and category:
            self.queryset = self.queryset.filter(followed_by__gte=int(min_range),
                                                 followed_by__lte=int(max_range),
                                                 type=category).order_by('created_at')
        elif min_range and max_range:
            self.queryset = self.queryset.filter(followed_by__gte=int(min_range),
                                                 followed_by__lte=int(max_range)).order_by('created_at')

        elif min_range and category:
            self.queryset = self.queryset.filter(followed_by__gte=int(min_range),
                                                 type=category).order_by('created_at')

        elif min_range:
            self.queryset = self.queryset.filter(followed_by__gte=int(min_range)).order_by('created_at')

        elif category:
            self.queryset = self.queryset.filter(type=category).order_by('created_at')

        return self.queryset



class CustomProductList(generics.ListAPIView):

    serializer_class = CustomProductSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LargeResultsSetPagination
    queryset = CustomProduct.objects.filter(is_active=True).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        min_range = self.request.query_params.get('min_range', None)
        max_range = self.request.query_params.get('max_range', None)
        order = self.request.query_params.get('order_by', None)



        if (min_range and max_range):
            self.queryset = self.queryset.filter(selling_price__range=(min_range, max_range))
        elif (min_range and not max_range):
            self.queryset = self.queryset.filter(selling_price__gte=min_range)

        if (order):
            # lp = lowest price
            # hp = highest price
            # da = date added price

            if(order == 'lp'):
                self.queryset = self.queryset.order_by('selling_price')
            elif (order == 'hp'):
                self.queryset = self.queryset.order_by('-selling_price')
                # elif (order == 'da'):
                #     self.queryset = self.queryset.order_by('-created_at')

        return self.queryset


class FeedBackView(APIView):

    def post(self, request, format=None):
        response = {}
        try:
            # feedback = FeedBack.objects.filter(email=request.data['email']).exists()
            # if feedback:
            #     response.update({'feedback': "Feedback already exists."})
            #     status_code = status.HTTP_409_CONFLICT
            FeedBack.objects.create(email=request.data['email'],
                                    feedback=request.data['comment'])
            response.update({'success':True})
            status_code = status.HTTP_201_CREATED
        except Exception as e:
            response.update({'success': False})
            status_code = status.HTTP_403_FORBIDDEN

        return Response(response, status=status_code)


class InfluencerCategory(generics.ListAPIView):

    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Influencer.objects.values('type').distinct()
        return queryset


class KeywordProductView(APIView):

    def post(self, request, format=None):
        data = self.request.data['title']
        qs = Keyword.objects.filter(product__title=data)
        serializer = KeywordSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoGroupView(generics.ListAPIView):
    """View to list training video groups.
    Args:
        :param generics.LISTAPIView: Inherit Base Mixin.
    Returns:
        queryset: Contains all groups details.
    """

    serializer_class = VideoGroupSerializer

    def get_queryset(self):
        queryset = VideoGroup.objects.filter(is_active=True)
        return queryset


class TrainingVideoView(generics.ListAPIView):
    """View to list training video.
    Args:
        :param generics.LISTAPIView: Inherit Base Mixin.
    Returns:
        queryset: Contains all videos related to group name.
    """

    serializer_class = TrainingVideoSerializer

    def get_queryset(self):
        queryset = TrainingVideo.objects.filter(is_active=True).order_by('-created_at')
        return queryset


class BookmarkProductsView(APIView):
    """
       Save/Delete and List bookmarked products.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        qs = BookmarkedProducts.objects.filter(user=request.user)
        serializer = BookmarkProductSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        response = {}
        req_data = request.data
        data = req_data['product']
        type = req_data['type']

        product = {
            'user': request.user,
            'title': '',
            'type': '',
            'description': '',
            'img_link': '',
            'vendor': '',
            'product_link': '',
            'price': '',
            'published_at': '',
            'grams': '',
            'unit': '',
        }

        if type == 'explore':
            product = self.map_parsed_product(data, product)
        elif type == 'hot':
            product = self.map_hot_product(data, product)
        elif type == 'feed':
            product = self.map_feed_product(data, product)




        qs = BookmarkedProducts.objects.filter(user=request.user,
                                               title = product['title']).exists()
        if qs is False:
            try:
                created_product = BookmarkedProducts(**product)
                created_product.save()
                response.update({'success':True})
                status_code = status.HTTP_201_CREATED
            except Exception as e:
                response.update({'success': False})
                status_code = status.HTTP_403_FORBIDDEN
            return Response(response, status=status_code)
        else:
            return Response(status=status.HTTP_202_ACCEPTED)

    def get_object(self, pk):
        try:
            return BookmarkedProducts.objects.get(id=pk, user=self.request.user)
        except BookmarkedProducts.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        qs = self.get_object(pk)
        qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def map_parsed_product(self, data, product):
        try:
            product['title'] = data['title']
            product['type'] = data['type']
            product['description'] = data['details']
            product['img_link'] = data['img_src']
            product['vendor'] = data['vendor']
            product['product_link'] = data['product_link']
            product['price'] =  data['s_variants']['price']
            product['published_at'] = data['s_variants']['published']
            product['grams'] = data['s_variants']['grams']
            product['unit'] = data['s_variants']['unit']
        except Exception as e:
            logger.debug('product mapping error {0}', e)

        return product

    def map_hot_product(self, data, product):
        try:
            product['title'] = data['title']
            product['type'] = data['type']
            product['description'] = data['description']
            product['img_link'] = data['image']
            product['vendor'] = data['vendor']
            product['product_link'] = data['product_link']
            product['price'] = data['actual_price']
            product['published_at'] = data['released_date']
        except Exception as e:
            logger.debug('product mapping error {0}', e)

        return product

    def map_feed_product(self, data, product):
        try:
            product['title'] = data['title']
            product['type'] = data['type']
            product['description'] = data['description']
            product['img_link'] = data['img_link']
            product['vendor'] = data['vendor']
            product['product_link'] = data['product_link']
            product['price'] = data['price']
            product['published_at'] = data['published_at']
            product['grams'] = data['grams']
            product['unit'] = data['unit']
        except Exception as e:
            logger.debug('product mapping error {0}', e)

        return product


class ClickFunnelUserCreate(APIView):
    """Create user by getting its email from
       webhook send by click funnels on
       purchase and send email to user for password set.

       :param APIVIEW: Inherit generic view.
       :return response: created user with email sent.
    """
    http_method_names = ['post']

    def post(self, request):
        data = request.data # get data object from request.
        user = self.create_temp_user(data)
        data = dict(email=data['email'])
        if user is not None:
            serializer = CustomUserCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response("User created successfully.", status=status.HTTP_201_CREATED)
        else:
            return Response("User already Exist.", status=status.HTTP_202_ACCEPTED)

    def create_temp_user(self, data):
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        user = User.objects.filter(email=data['email'])
        if user.exists() is False:
            random_data = os.urandom(128)
            temp_pwd = hashlib.md5(random_data).hexdigest()[:8]
            user = User.objects.create_user(email=data['email'], password=temp_pwd)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            email_address = EmailAddress()
            email_address.user = user
            email_address.verified = True
            email_address.primary = True
            email_address.email = data['email']
            email_address.save()
            return user
        return None


class FeedlyView(APIView):
    """User list, save and delete their searched store
       from feedStore model.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        feeds = FeedStore.objects.filter(user=request.user)
        serializer = FeedStoreSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        response = {}
        feeds_count = FeedStore.objects.filter(user=request.user).count()
        if feeds_count < 10:
            try:
                FeedStore.objects.create(user=request.user,
                                         feed_id = request.data['id'],
                                         brand_url = request.data['brand_url'],
                                         brand_name = request.data['brand-name'],
                                         )
                RssFeed.objects.filter(id=request.data['id']).update(saved_feed=True)
                response.update({'success':True})
                status_code = status.HTTP_201_CREATED
            except Exception as e:
                response.update({'success': False})
                status_code = status.HTTP_403_FORBIDDEN
        else:
            response.update({'Message': "You have reached maximium limit to add store into your feeds."})
            status_code = status.HTTP_200_OK

        return Response(response, status=status_code)

    def get_object(self, pk):
        try:
            return FeedStore.objects.get(feed_id=pk, user=self.request.user)
        except RssFeed.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        RssFeed.objects.filter(pk=pk).update(saved_feed=False)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TrainingVideoDetailView(generics.ListAPIView):
    """View to list detail of training video.
    Args:
        :param generics.LISTAPIView: Inherit Base Mixin.
    Returns:
        queryset: Contains video related to group name.
    """

    serializer_class = TrainingVideoSerializer

    def get_queryset(self):
        video_id = self.request.query_params['id']
        if video_id is not None:
            queryset = TrainingVideo.objects.filter(pk=int(video_id), is_active=True)
        else:
            queryset = TrainingVideo.objects.none()
        return queryset


class ProductsFeedView(generics.ListAPIView):
    """List all products of requested store."""

    serializer_class = ProductFeedSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = FeedProducts.objects.filter(user=self.request.user.id).order_by('created_at')
        return queryset
