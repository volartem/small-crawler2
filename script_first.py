import requests
from scrapy.http import TextResponse
import csv


def get_links(url, proxy='your_proxy_here_with_port'):
    proxy_dict = {
        # 'https': '',
        'http': proxy,
    }
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.21 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8'
    }
    link_list = []

    r = session.request('GET', url, headers=headers, proxies=proxy_dict, timeout=1)
    response = TextResponse(r.url, body=r.text, encoding='utf-8')
    last_page_index = int(response.xpath('.//ul[@class="pagination__list"]/'
                                         'li[@class="pagination__list__item"]/a/text()')[3].extract())
    page_num = 1
    while page_num <= last_page_index:
        if page_num != 1:
            r = session.request('GET', '{0}?page={1}'.format(url, page_num), headers=headers, proxies=proxy_dict)
            response = TextResponse(r.url, body=r.text, encoding='utf-8')
        for quote in response.xpath('//div[@class="single_list_item"]'):
            link_list.append({
                'link': quote.xpath('.//div[@class="single_list_item__company"]/a/@href').extract_first(),
                'name': quote.xpath('.//div[@class="single_list_item__company"]/a/text()').extract_first().strip(),
                'id': quote.xpath('.//div[@class="single_list_item__fiscal"]/span/text()').extract_first(),
                'date': quote.xpath('.//div[@class="single_list_item__subscribe_date"]/strong/text()').extract_first(),
            })
        print(page_num)
        page_num += 1
    return link_list


def main():
    link_dict = get_links('https://www.fazland.com/elenco-aziende')
    with open('links.csv', 'w') as f:
        wtr = csv.writer(f)
        for line in link_dict:
            wtr.writerow(['https://www.fazland.com{}'.format(line.get('link')),
                          line.get('name'), line.get('id'), line.get('date')])

if __name__ == '__main__':
    main()
