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
                try:
                    _store_urls = FeedStore.objects.filter(user_id = user.user_id)
                    _urls_count = _store_urls.count()

                    for url_obj in _store_urls:
                        url = url_obj.brand_url+"/collections/all.atom"
                        try:
                            req = urllib.request.Request(url, None, headers)
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
                        if 'entry' in pars_response['feed']:
                            try:
                                for content in pars_response['feed']['entry']:
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
                                    check = FeedProducts.objects.filter( user_id = user.user_id,
                                                                         title = content['title'],
                                                                         type = content['s:type']).exists()
                                    if not check:
                                        FeedProducts.objects.create( user_id = user.user_id,
                                                                     store_id = url_obj.id,
                                                                     title = content['title'],
                                                                     type = content['s:type'],
                                                                     vendor = content['s:vendor'],
                                                                     img_link = src,
                                                                     product_link = content['link']['@href'],
                                                                     description = desc,
                                                                     price = price,
                                                                     grams = grams,
                                                                     unit = unit,
                                                                     published_at = published
                                                                     )
                                print("Successfully inserted {0} products.".format(url_obj))
                            except Exception as e:
                                print("Error on inserting product detail.")
                                print('Reason', e.reason)
                                continue
                        else:
                            print("Feeds has no entries.")
                            continue
                except Exception as e:
                    print("Error:"+str(e))
                    print('At Url {0}.'.format(url_obj.brand_url))
                    cron.delete()
                    raise CommandError(e)

            print("Inserted" + ' ' + str(_urls_count) + '  ' + "products details Successfully.")
            cron.delete()
            end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
            total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
            self.stdout.write('The task took {0} second !'.format(total_time))
        else:
            self.stdout.write("Previous task is in progress yet. We are not starting new task.")