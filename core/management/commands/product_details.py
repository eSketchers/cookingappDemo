from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import urllib.request
import datetime
import time
import xmltodict
from core.models import StoreUrl, ProductDetail


class Command(BaseCommand):
    help = 'Scrape Product details from urls store in Stores.'

    def handle(self, *args, **options):
        user_id = 4
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('The script start time: {0} '.format(start_time))
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        try:
            _store_urls = StoreUrl.objects.filter(user_id = user_id, get_product=False)
            _urls_count = _store_urls.count()

            for url_obj in _store_urls:
                url = "https://"+url_obj.url+"/collections/all.atom"
                try:
                    req = urllib.request.Request(url,None,headers)
                    with urllib.request.urlopen(req) as response:
                        response = response.read()
                except urllib.request.HTTPError as e:
                    if hasattr(e, 'reason'):
                        print('HTTP ERROR {0}'.format(url_obj.url))
                        print('Reason: ', e.reason)
                    continue
                except urllib.request.URLError as e:
                    if hasattr(e, 'reason'):
                        print('Response ERROR {0}'.format(url_obj.url))
                        print('Reason: ', e.reason)
                    continue
                except Exception as e:
                    if hasattr(e, 'reason'):
                        print('Exception ERROR of {0}'.format(url_obj.url))
                        print('Reason: ', e.reason)
                    continue

                pars_response = xmltodict.parse(response)
                if pars_response['feed']['entry']:
                    for content in pars_response['feed']['entry']:
                        soup = BeautifulSoup(content['summary']['#text'], 'html.parser')
                        tb_data = soup.find('table').find_all('tr')[1].find('td')
                        desc = tb_data.text
                        # p_tag = tb_data.find_all("p", limit=1)
                        #
                        # if p_tag.__len__() == 0:
                        #     description = tb_data.get_text()
                        # else:
                        #     description = p_tag[0].get_text()
                        try:
                            ProductDetail.objects.create(title = content['title'],
                                                         type = content['s:type'],
                                                         vendor = content['s:vendor'],
                                                         description = desc )
                        except Exception as e:
                            print("Error on inserting product detail.")
                            print('Reason',e.reason)
                            continue

                    # make url get product field True.
                    url_obj.get_product = True
                    url_obj.save()
                    print("Successfully inserted {0} products.".format(url_obj.url))
                else:
                    print("Feeds has no entries.")
                    continue

        except Exception as e:
            print("Error:"+str(e))
            print('At Url {0}.'.format(url_obj.url))
            raise CommandError(e)

        print("Inserted" + ' ' + str(_urls_count) + '  ' + "products details Successfully.")
        end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
        self.stdout.write('The script took {0} second !'.format(total_time))