from rest_framework.views import APIView
import urllib.request
import xmltodict
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.response import Response
import json

# Create your views here.


class ListData(APIView):

    def post(self, request):
        result = []
        variants = []
        product_details = {}
        url = request.data['link']
        page_res = self.get_page(url)
        if page_res:
            for content in page_res['feed']['entry']:
                soup = BeautifulSoup(content['summary']['#text'], 'html.parser')
                img_tag = soup.find_all("img")
                src = img_tag[0].attrs['src']
                table = soup.find('table')
                row = table.find_all('tr')[1]
                data = row.find('td')
                p_tag = data.find_all("p", limit=2)
                if len(p_tag) == 2:
                    para_tag = str(p_tag[0]) + str(p_tag[1])
                elif len(p_tag) == 1:
                    para_tag = str(p_tag[0])
                else:
                    para_tag = data.find('p')
                if isinstance(content['s:variant'], list):
                    variants = []
                    variants.append(content['s:variant'])
                else:
                    product_details = { 'sku': content['s:variant']['s:sku'], 'grams': content['s:variant']['s:grams'],
                                  'price': content['s:variant']['s:price']['@currency'] + ' ' + content['s:variant']['s:price']['#text']
                                }
                data = {
                    'img_src' : src,
                    'product_link':content['link']['@href'],
                    'details' : para_tag,
                    'title': content['title'],
                    'vendor'  : content['s:vendor'],
                    'type'    : content['s:type'],
                    's_variants': product_details,
                    'mul_variants': variants
                }
                result.append(data)
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
