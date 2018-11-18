from decimal import Decimal

from bs4 import BeautifulSoup


class ShopParser:

    def __init__(self, price_threshold):
        self.price_threshold = price_threshold

    def parse_content(self, content, parser_string):
        soup = BeautifulSoup(content, 'html.parser')
        samples = self.get_samples(soup)
        alerts = []
        for sample in samples:
            price = self.parse_price(sample)
            print(price)
            if price < self.price_threshold:
                msg = f'ALERT! Product found for {price} in {parser_string}.'
                print(msg)
                alerts.append(msg)
        return alerts

    def get_samples(self, soup):
        raise NotImplementedError()

    def parse_price(self, sample):
        raise NotImplementedError()


class XKomShopParser(ShopParser):

    def get_samples(self, soup):
        return soup.find_all('span', class_='price')

    def parse_price(self, sample):
        price = sample.string.strip().replace(' ', '').replace('zł', '')
        return Decimal(price.replace(',', '.'))


class MediaExpertShopParser(ShopParser):

    def get_samples(self, soup):
        return soup.find_all('p', class_='price')

    def parse_price(self, sample):
        price = sample.get_text().replace(' ', '').strip()[:-2]
        return Decimal(price)


class EuroRTVAGDShopParser(ShopParser):

    def get_samples(self, soup):
        return soup.select(
            'div#product-category-new > div.product-price > div.price-normal'
        )

    def parse_price(self, sample):
        price = sample.get_text().replace('zł', '').replace(' ', '').strip()
        return Decimal(price.replace(u'\xa0', ''))


class MediaMarktShopParser(ShopParser):

    def get_samples(self, soup):
        return soup.find_all(
            'a',
            attrs={'class': 'm-offerBox_basket', 'data-offer-outlet': 'no'}
        )

    def parse_price(self, sample):
        price = sample.attrs['data-price']
        return Decimal(price)
