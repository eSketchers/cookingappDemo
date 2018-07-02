from bs4 import BeautifulSoup
import urllib.request
import time

from core.models import StoreUrl


def main():
    business_type = 21 # on exchange.shopfiy: business_type of dropshipping is:21
    user_id = 3
    for page in range(1, 6):
        link = "https://exchange.shopify.com/shops?business_types="+str(business_type)+"&page="+str(page)
        try:
            req = urllib.request.Request(link)
            with urllib.request.urlopen(req) as response:
                response = response.read()
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
                print("Inserted first url Successfully.")
        except Exception as e:
            print("Error Occur:")
            print(e)
            return e
        print("Inserted" + str(page) + "urls Successfully.")
    return True


if __name__ == "__main__":
    print("Executing....")
    startTime = time.time()
    print('The script start time:{0}'.format(startTime))
    exec_ret = main()
    if exec_ret is True:
        print("Success.")
    else:
        print(exec_ret)
    print('The script took {0} second !'.format(time.time() - startTime))