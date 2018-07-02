from bs4 import BeautifulSoup
import urllib.request
import xmltodict

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dropshipping.settings")

application = get_wsgi_application()

from core.models import StoreUrl


class GetProduct(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.get_feeds()
        pass

    def get_feeds(self):
        try:
            _store_urls = StoreUrl.objects.filter(user_id = self.user_id)
        except Exception as e:
            print(e.message)
            pass

        for url_obj in _store_urls:
            try:
                url = "https://"+url_obj.url+"/collections/all.atom"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req) as response:
                    response = response.read()
                pars_response = xmltodict.parse(response)

                for content in pars_response['feed']['entry']:
                    soup = BeautifulSoup(content['summary']['#text'], 'html.parser')
                    img_tag = soup.find_all("img")[0].attrs['src']
                    tb_data = soup.find('table').find_all('tr')[1].find('td')
                    p_tag = tb_data.find_all("p", limit=1)

                    if p_tag.__len__() == 0:
                        description = tb_data.get_text()
                    else:
                        description = p_tag

                    print(description)
                    pass
            except Exception as e:
                print("urllib:"+str(e))
                pass

        return True


object_call = GetProduct(3)