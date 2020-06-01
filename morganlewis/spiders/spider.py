import scrapy
import math
from datetime import datetime

from morganlewis.items import Product


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    url = 'https://www.morganlewis.com/api/custom/peoplesearch/search?keyword=&category=bb82d24a9d7a45bd938533994c4e775a&sortBy=lastname&numberPerPage=50&numberPerSection=5&enforceLanguage=&languageToEnforce=&school=&position=&location=&court=&judge=&isFacetRefresh=true&pageNum={}'

    url_publications = 'https://www.morganlewis.com/api/sitecore/accordion/getaccordionlist'

    post_data_publications = {
        "itemID": "",
        "itemType": "publicationitemlist",
        "printView": ""
    }

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.url.format(1))

    def parse(self, response):
        total_count = response.xpath('//div[@class="c-results__listing js-results-list"]/@data-total').extract_first()
        pages = int(math.ceil(float(total_count) / 50)) + 1
        for page in range(1, pages): yield scrapy.Request(url=self.url.format(str(page)), callback=self.get_links,
                                                          dont_filter=True)

    def get_links(self, response):
        urls = response.xpath('//div[@class="c-content_team__card-info"]/a/@href').extract()
        for url in urls: yield scrapy.Request(url=response.urljoin(url), callback=self.load_publications)

    def load_publications(self, response):
        body = self.post_data_publications
        body['itemID'] = str(response.text.split('itemID: "')[1].split('"')[0])
        yield scrapy.Request(url=self.url_publications, method='POST', callback=self.get_publications,
                             headers=self.headers, body=str(body), meta={'url': response.url})

    def get_publications(self, response):
        publications = []
        for title in response.xpath('//p/a/@title').extract(): publications.append(title)
        yield scrapy.Request(url=response.meta['url'], callback=self.parse_product, dont_filter=True,
                             meta={'publications': publications})

    def parse_product(self, response):
        item = Product()
        item['name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
        item['photo'] = response.urljoin(response.xpath('//img[@itemprop="image"]/@src').extract_first())
        item['url'] = response.url
        item['position'] = response.xpath('//section[@class="person-heading"]/h2/text()').extract_first()
        item['phone'] = response.xpath('//p[@itemprop="telephone"]/a/text()').extract_first()
        item['email'] = response.xpath('//a[@itemprop="email"]/text()').extract_first()
        item['services'] = []
        for service in response.xpath('//section[@class="person-depart-info"]/ul/li/a/@title').extract():
            item['services'].append(service)
        item['sectors'] = []
        for service in response.xpath('//div[@class="person-depart-info"]/ul/li/a/@title').extract():
            item['sectors'].append(service)
        item['brief'] = response.xpath('//meta[@name="description"]/@content').extract_first()
        item['datetime'] = datetime.now().strftime("%H:%M:%S")
        item['publications'] = response.meta['publications']
        yield item
