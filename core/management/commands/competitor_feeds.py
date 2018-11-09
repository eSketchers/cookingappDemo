from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import urllib.request
import datetime
import xmltodict
from core.models import FeedStore,FeedProducts, CronStatus
from accounts.models import EmailAddress

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }


class Command(BaseCommand):
    help = 'Scrape product from user feeds store and save in table.'

    def handle(self, *args, **options):
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('Task start time: {0} '.format(start_time))
        cron_name = "Get user feed products."
        cron, created = CronStatus.objects.get_or_create(job_name = cron_name)
        if created:
            users = EmailAddress.objects.filter(verified = True, user__is_admin = False)
            for user in users:
                print('----------------------------')
                print('Executing for user {0}'.format(user.email))
                _store_urls = FeedStore.objects.filter(user_id=user.user_id)
                _urls_count = _store_urls.count()
                for url_obj in _store_urls:
                    response = self.parse_url(url_obj)
                    if not response:
                        continue
                    else:
                        try:
                            pars_response = xmltodict.parse(response)
                        except Exception as e:
                            print('Exception ERROR of: {0} for the reason: {1}'.format(url_obj.brand_url, e))
                            continue
                        self.parse_product(pars_response, user, url_obj)
            cron.delete()
            end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
            total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
            self.stdout.write('The task took {0} second !'.format(total_time))
        else:
            self.stdout.write("Previous task is in progress yet. We are not starting new task.")

    def parse_url(self, url_obj):
        url = url_obj.brand_url + "/collections/all.atom"
        response = None
        try:
            req = urllib.request.Request(url, None, headers)
            with urllib.request.urlopen(req) as response:
                return response.read()
        except urllib.request.HTTPError as e:
            if hasattr(e, 'reason'):
                print('HTTP ERROR from: {0} for the reason: {1}'.format(url, e.reason))
        except urllib.request.URLError as e:
            if hasattr(e, 'reason'):
                print('Response ERROR from: {0} for the reason: {1}'.format(url, e.reason))
        except Exception as e:
            print('Exception ERROR of: {0} for the reason: {1}'.format(url, e))
        return response

    def parse_product(self, feeds, user, url_obj):
        if 'entry' in feeds['feed']:
            try:
                count = 0
                for content in feeds['feed']['entry']:
                    soup = BeautifulSoup(content['summary']['#text'], 'html.parser')
                    src = soup.find_all("img")[0].attrs['src']
                    tb_data = soup.find('table').find_all('tr')[1].find('td')
                    desc = tb_data.text
                    if isinstance(content['s:variant'], list):
                        price = float(content['s:variant'][0]['s:price']['#text'])
                        unit = content['s:variant'][0]['s:price']['@currency']
                        grams = content['s:variant'][0]['s:grams']
                        published = content['published']
                    else:
                        price = float(content['s:variant']['s:price']['#text'])
                        unit = content['s:variant']['s:price']['@currency']
                        grams = content['s:variant']['s:grams']
                        published = content['published']

                    # Check Products exits already.
                    check = FeedProducts.objects.filter(user_id=user.user_id,
                                                        title=content['title'],
                                                        type=content['s:type']).exists()
                    if not check:
                        FeedProducts.objects.create(user_id=user.user_id,
                                                    store_id=url_obj.id,
                                                    title=content['title'],
                                                    type=content['s:type'],
                                                    vendor=content['s:vendor'],
                                                    img_link=src,
                                                    product_link=content['link']['@href'],
                                                    description=desc,
                                                    price=price,
                                                    grams=grams,
                                                    unit=unit,
                                                    published_at=published
                                                    )
                        count += 1
                print("Successfully inserted {0} products from store.".format(count))
            except Exception as e:
                print("Error on inserting product detail for store {0}.".format(url_obj.brand_url))
                print('Reason', e)
        else:
            print("Feeds has no entries.")


