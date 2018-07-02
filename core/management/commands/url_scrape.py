from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import urllib.request
import datetime
import time
from core.models import StoreUrl


class Command(BaseCommand):
    help = 'Scrape drop shipping sites urls from Exchange Shopify.'

    def handle(self, *args, **options):
        business_type = 21  # on exchange.shopfiy: business_type of dropshipping is:21
        user_id = 4
        print("Executing....")
        start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        print('The script start time: {0}'.format(start_time))
        for page in range(1, 6):
            link = "https://exchange.shopify.com/shops?business_types=" + str(business_type) + "&page=" + str(page)
            try:
                user_agent = 'Mozilla/5.0 (Windows; U; ' \
                             'Windows NT 5.1; en-US; rv:1.9.0.7) ' \
                             'Gecko/2009021910 Firefox/3.0.7'
                headers = {'User-Agent': user_agent, }
                try:
                    req = urllib.request.Request(link,None,headers)
                    with urllib.request.urlopen(req) as response:
                        response = response.read()
                except urllib.request.HTTPError as e:
                    if hasattr(e, 'reason'):
                        print('HTTP ERROR.')
                        print('Reason: ', e.reason)
                    continue
                except urllib.request.URLError as e:
                    if hasattr(e, 'reason'):
                        print('Response ERROR.')
                        print('Reason: ', e.reason)
                    continue
                except Exception as e:
                    if hasattr(e, 'reason'):
                        print('Response ERROR.')
                        print('Reason: ', e.reason)
                    continue

                soup = BeautifulSoup(response, "html.parser")
                site_card = soup.find_all("div", "layout-fill-space shop-tile")

                print("Start getting data from html page.")

                for card in site_card:
                    url = card.find("p", "shop-tile__url")
                    title = card.find("p", "shop-tile__title").get_text()
                    revenue = card.find("span", "shop-tile__metric__value text-bold").get_text()
                    if not url.get_text() == "URL Hidden":
                        pars_url = url.get_text()
                        if url.get_text().startswith('www.'):
                            pars_url = url.get_text().split('.', 1)[1]

                        # Save stores data in model.
                        StoreUrl.objects.create(user_id=user_id,
                                                title=title,
                                                url=pars_url,
                                                revenue=revenue)
                print("Inserted url Successfully.")
            except Exception as e:
                print("Error Occur:")
                print(e)
                raise CommandError(e)

        print("Inserted" +' '+ str(page) +'  ' +"urls Successfully.")
        end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        total_time = (datetime.datetime.strptime(end_time, '%H:%M:%S') - datetime.datetime.strptime(start_time, '%H:%M:%S'))
        self.stdout.write('The script took {0} second !'.format(total_time))
