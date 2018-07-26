# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import json
import datetime, time
from core.models import Influencer
import requests
from lxml.html import fromstring
import urllib.request
from itertools import cycle
from bs4 import BeautifulSoup
from random import choice


user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }

access_token = "8280489681.984e030.1dec9d914e61485c8a0008fac50628af"
client_id = "984e030d3d144e64bebde49e0e839bd6"


class Command(BaseCommand):
    help = 'Scrape influencer data from instagram.'

    def handle(self, *args, **options):
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('The script start time: {0}'.format(start_time))

        try:
            proxies = self.get_proxies()
            # proxy_pool = cycle(proxies)

            queryset = Influencer.objects.filter(info=False)

            for result in queryset:
                # proxy = next(proxy_pool)
                proxy_pool = choice(proxies)
                print("Request of {}" .format(result.url))
                try:
                    response = requests.get(result.url, proxies={"http": proxy_pool, "https": proxy_pool})
                    soup = BeautifulSoup(response.content, "html.parser")
                    body = soup.find('body')
                    script_tag = body.find('script')
                    raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
                    js_data = json.loads(raw_string)
                    user_data = js_data['entry_data']['ProfilePage'][0]['graphql']['user']
                    if user_data['external_url']:
                        Influencer.objects.filter(url=result.url, info = False).update(
                            biograpghy=user_data['biography'],
                            external_link = user_data['external_url'],
                            name = user_data['full_name'],
                            username = user_data['username'],
                            profile_pic = user_data['profile_pic_url'],
                            profile_pic_hd = user_data['profile_pic_url_hd'],
                            follow = user_data['edge_follow']['count'],
                            followed_by = user_data['edge_followed_by']['count'],
                            info=True
                        )
                    else:
                        Influencer.objects.filter(url=result.url).update(
                            biograpghy=user_data['biography'],
                            name=user_data['full_name'],
                            username=user_data['username'],
                            profile_pic=user_data['profile_pic_url'],
                            profile_pic_hd=user_data['profile_pic_url_hd'],
                            follow=user_data['edge_follow']['count'],
                            followed_by=user_data['edge_followed_by']['count'],
                            info = True
                        )
                except Exception as e:
                    print("Error from loop.")
                    print(e)
                    continue
                time.sleep(15)
        except Exception as e:
            print("Error Occur:")
            raise CommandError(e)

        end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
        self.stdout.write('The script took {0} second !'.format(total_time))

    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        try:
            req = urllib.request.Request(url, None, headers)
            with urllib.request.urlopen(req) as response:
                response = response.read()
            parser = fromstring(response.decode('utf-8'))
            proxies = []
            for i in parser.xpath('//tbody/tr')[:80]:
                if i.xpath('.//td[7][contains(text(),"yes")]'):
                    proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                    proxies.append(proxy)
            return proxies
        except Exception as e:
            print("Error from get proxies function."+e)