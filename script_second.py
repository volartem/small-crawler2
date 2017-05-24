# from get_proxy import get_proxy_list
import csv
import requests
from scrapy.http import TextResponse


# TODO: method for rebuild
def proxy_in_scraper(session, headers, link, proxy_dict):
    r = session.request('GET', link.get('link'), headers=headers, proxies=proxy_dict)
    response = TextResponse(r.url, body=r.text, encoding='utf-8')
    description = response.xpath('//div[@class="page_companies_profile__bio"]//p/text()').extract_first()
    link['description'] = description
    link['description_count'] = len(description) or 0
    link['q_dipendenti'] = ''


def get_full_info(list_dict, proxy='your_proxy_here_with_port'):
    # TODO: rebuild for multi-proxy use from proxy spider
    # proxy_list = get_proxy_list()
    # for proxy in proxy_list:
    #     proxyDict = {
    #         'http': '{0}:{1}'.format(proxy['ip'], proxy['port']),
    #     }
    proxy_dict = {
        'http': proxy,
    }
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.21 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8'
    }
    count = 0
    for link in list_dict[:50]:
        r = session.request('GET', link.get('link'), headers=headers, proxies=proxy_dict)
        response = TextResponse(r.url, body=r.text, encoding='utf-8')
        description = response.xpath('//div[@class="page_companies_profile__bio"]//p/text()')
        link['description'] = description.extract_first().strip() if description else ''
        link['description_count'] = len(link['description']) or 0
        q_dipendenti = [row.xpath('./div[@class="col-sm-8"]/p[@class="secondary text-left"]/text()').extract_first()
                        for row in response.xpath('//div[@id="widgets"]/div[@class="row"]')
                        if row.xpath('.//p[@class="gray-dark"]/b/text()').extract_first() ==
                        'Quanti dipendenti/collaboratori lavorano in Azienda?']
        link['q_dipendenti'] = q_dipendenti[0] if len(q_dipendenti) > 0 else ''
        q_commesse = [row.xpath('./div[@class="col-sm-8"]/p[@class="secondary text-left"]/text()').extract_first()
                      for row in response.xpath('//div[@id="widgets"]/div[@class="row"]')
                      if row.xpath('.//p[@class="gray-dark"]/b/text()').extract_first() ==
                      'Quante commesse svolgete in un anno circa?']
        link['q_commese'] = q_commesse[0] if len(q_commesse) > 0 and q_commesse[0] != '--' else ''
        link['categories'] = [row.xpath('text()').extract_first()
                              for row in response.xpath('.//span[@itemprop="name"]')]
        link['categories_count'] = len(link['categories'])
        link['address'] = response.xpath('//div[@class="company_venue__text"]/span[@itemprop="streetAddress"]/text()').extract_first()
        hired = response.xpath('//div[@class="job_assigned__row"]')
        link['hired'] = 'Yes' if hired else 'No'
        link['count_hired'] = response.xpath('//div[@class="job_assigned__number"]/span/text()').extract_first() if hired else 0
        link['review'] = 'Yes' if response.xpath('//*[contains(text(), "Valutazione dei clienti")]') else 'No'
        score = response.xpath('//div[@class="company_evaluation__points"]/dl/dd/text()')
        link['score_comunicazione'] = score[0].extract() if link['review'] == 'Yes' else ''
        link['score_coerenza'] = score[1].extract() if link['review'] == 'Yes' else ''
        link['score_puntualita'] = score[2].extract() if link['review'] == 'Yes' else ''
        link['score_qualita'] = score[3].extract() if link['review'] == 'Yes' else ''
        link['progetti'] = 'Yes' if response.xpath('//*[contains(text(), "Progetti recenti")]') else 'No'
        count += 1
        print('__', count)
    return list_dict


def main():
    reader = csv.reader(open('links.csv'), delimiter=',', quotechar='"')
    links_list = []
    for row in reader:
        links_list.append({
            'link': row[0],
            'name': row[1],
            'id': row[2],
            'date': row[3],
        })
    links_list = get_full_info(links_list)
    with open('output.csv', 'w') as f:
        wtr = csv.writer(f, delimiter=',')
        wtr.writerow(['Name (text)', 'Data registrazione (text)', 'P. IVA (text)',
                      'Description (text)', 'Description Count of charaters', 'Quanti dipendenti?',
                      'Quante commesse?', 'Categories (text)', 'Count of Categories',
                      'Address (text)', 'Hired (yes/no)', 'Count of hired (number)', 'Review yes/no',
                      'Avg. score "Comunicazione"', 'Avg. score "Coerenza"', 'Avg. score "Puntualitá"',
                      'Avg. score "Qualitá"', 'Progetti (yes/no)', 'Source link'])
        for link in links_list:
            wtr.writerow([link['name'], link['date'], link['id'],
                          link['description'], link['description_count'], link['q_dipendenti'],
                          link['q_commese'], link['categories'], link['categories_count'], link['address'],
                          link['hired'], link['count_hired'], link['review'], link['score_comunicazione'],
                          link['score_coerenza'], link['score_puntualita'], link['score_qualita'],
                          link['progetti'], link['link']])


if __name__ == '__main__':
    main()
