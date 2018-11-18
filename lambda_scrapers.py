import os

import boto3
import requests
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup

import basic


TO_SCRAPE_EXAMPLE = {
    'addresses': {
        'XKomShop': (
            'https://www.x-kom.pl/szukaj?q=samsung_s8&per_page=90&f[groups][4]'
            '=1&f[categories][1590]=1&f[manufacturers][29]=1&f[193][62726]=1'
        ),
        'MediaExpertShop': (
            'https://www.mediaexpert.pl/lista,samsunga-galaxy-s8'
        ),
        'EuroRTVAGDShop': (
            'https://www.euro.com.pl/search/telefony-komorkowe.bhtml'
            '?keyword=samsung%20galaxy%20s8%20sm-g950'
        ),
        'MediaMarktShop': (
            'https://mediamarkt.pl/search?query[menu_item]=25983'
            '&query[querystring]=samsung%20s8'
        )
    },
    'price_threshold': 2200
}


parser_class = {
    'XKomShop': basic.XKomShopParser,
    'MediaExpertShop': basic.MediaExpertShopParser,
    'EuroRTVAGDShop': basic.EuroRTVAGDShopParser,
    'MediaMarktShop': basic.MediaMarktShopParser
}

HEADERS = {
    'user-agent': (
        'Mozilla/5.0 (X11; Linux x86_64 AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
    ),
    'referer': 'https://www.google.pl/',
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;'
        'q=0.9,image/webp,image/apng,*/*;q=0.8'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Pragma': 'no-cache'
}


def send_message(alerts):
    notification_email = os.environ.get('NOTIFY_EMAIL_ADDRESS', None)
    sender = os.environ.get('NOTIFY_SENDER_ADDRESS', None)

    if not (notification_email or sender):
        print('Cant send email!')
        return

    body = ''
    for msg in alerts:
        body += f'<p>{msg}</p>'
    body_html = """<html>
    <head></head>
    <body>
      <h1>Product price monitoring notification:</h1>
    """
    body_html += body + '</body></html>'
    body_text = BeautifulSoup(body_html, 'html.parser').text

    client = boto3.client('ses', region_name='eu-west-1')
    try:
        response = client.send_email(
            Destination={'ToAddresses': [notification_email]},
            Message={
                'Body': {
                    'Html': {'Charset': 'UTF-8', 'Data': body_html},
                    'Text': {'Charset': 'UTF-8', 'Data': body_text},
                },
                'Subject': {'Charset': 'UTF-8', 'Data': 'Product price alerts'}
            },
            Source=sender
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Email sent! Message ID:'),
        print(response['MessageId'])


def scrape(to_scrape):
    price_threshold = to_scrape['price_threshold']
    addresses = to_scrape['addresses']
    alerts = []
    for parser_string, url_address in addresses.items():
        print(f'Scraping {parser_string}.')
        response = requests.get(url_address, headers=HEADERS)
        if 200 <= response.status_code < 300:
            parser = parser_class[parser_string](price_threshold)
            result = parser.parse_content(response.content, parser_string)
            alerts.extend(result)
        else:
            print(f'Wrong response status {response.status_code}!')

    if alerts:
        send_message(alerts)


def handler(event, context):
    return scrape(event)


if __name__ == '__main__':
    scrape(TO_SCRAPE_EXAMPLE)
