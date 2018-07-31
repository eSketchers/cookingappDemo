from django.core.management.base import BaseCommand, CommandError
import urllib.request
import datetime
import xmltodict
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from core.models import ProductDetail, TrendingProduct, RssFeed, CronStatus
from accounts.models import EmailAddress


class Command(BaseCommand):
    help = 'Match products with products table and get similar title product.'

    def handle(self, *args, **options):
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('Task start time: {0} '.format(start_time))
        final_result = []
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        cron = CronStatus.objects.filter(status=True)
        if cron.exists():
            users = EmailAddress.objects.filter(verified = True, user__is_admin = False)
            for user in users:
                query = ProductDetail.objects.filter(user_id=user.user_id).values_list('title', flat=True).order_by('created_at')
                try:
                    rss_feed = RssFeed.objects.filter(user_id=user.user_id).values_list('brand_url', flat=True).order_by('created_at')
                    for url in rss_feed:
                        each_store = []
                        url = url + "/collections/all.atom"
                        try:
                            req = urllib.request.Request(url, None, headers)
                            with urllib.request.urlopen(req) as response:
                                response = response.read()
                        except urllib.request.HTTPError as e:
                            if hasattr(e, 'reason'):
                                print('HTTP ERROR {0}'.format(url))
                                print('Reason: ', e.reason)
                            continue
                        except urllib.request.URLError as e:
                            if hasattr(e, 'reason'):
                                print('Response ERROR {0}'.format(url))
                                print('Reason: ', e.reason)
                            continue
                        except Exception as e:
                            if hasattr(e, 'reason'):
                                print('Exception ERROR of {0}'.format(url))
                                print('Reason: ', e.reason)
                            continue

                        pars_response = xmltodict.parse(response)
                        if 'entry' in pars_response['feed']:
                            for content in pars_response['feed']['entry']:
                                soup = BeautifulSoup(content['summary']['#text'], 'html.parser')
                                src = soup.find_all("img")[0].attrs['src']
                                match_prd = []
                                get_product = process.extract(content['title'], query, scorer=fuzz.token_set_ratio)
                                for title, score in get_product:
                                    if score > 50:
                                        detail = ProductDetail.objects.filter(user_id = user.user_id, title__contains = title)
                                        if detail.exists():
                                            for det in detail:
                                                product = {'product': title,
                                                           'type':   det.type,
                                                           'vendor': det.vendor,
                                                           'image' : det.img_link,
                                                           'link':   det.product_link
                                                           }
                                                match_prd.append(product)
                                each_store.append({'main_title': content['title'],
                                                   'main_img': src,
                                                   'product': match_prd,
                                                   'link': content['link']['@href']
                                                   })
                            store = {"vendor":content['s:vendor'],
                                     "store": each_store
                                     }
                        final_result.append(store)
                    data = {'data': final_result}
                    obj_trend = TrendingProduct.objects.filter(user_id = user.user_id)
                    if obj_trend.exists():
                        TrendingProduct.objects.filter(user_id=user.user_id).update(data=data)
                    else:
                        TrendingProduct.objects.create(user_id=user.user_id, data=data)
                except Exception as e:
                    print("Error:" + str(e))
                    raise CommandError(e)
                    continue

            print("Inserted trending products json Successfully.")
            end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
            total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
            self.stdout.write('The task took {0} second !'.format(total_time))
            cron.delete()
        else:
            self.stdout.write('Product details scraping task is not completed yet.')