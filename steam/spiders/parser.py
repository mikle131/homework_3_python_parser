import scrapy
from urllib.parse import urlencode
from urllib.parse import urljoin

queries = ['Run', 'Anime', 'RPG', 'MMO']

class ParserSpider(scrapy.Spider):
    name = 'parser'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['http://store.steampowered.com/']

    def start_requests(self):
        for category in queries:
            for page in [1]:
                url = 'https://store.steampowered.com/search/?' + urlencode({'term': category, 'page': page})
                yield scrapy.Request(url, callback=self.parse_pages)
    
    def parse_pages(self, response):
        for href in response.xpath('//div[@id="search_resultsRows"]/a/@href').extract():
            pl = response.xpath(f'//div[@id="search_resultsRows"]/a[@href="{href}"]//div[@class="col search_name ellipsis"]//span//@class').extract()
            del pl[0]
            platforms = []
            for i in pl:
                platforms.append(i.split()[1])
            rev = response.xpath(f'//div[@id="search_resultsRows"]/a[@href="{href}"]//div[@class="col search_reviewscore responsive_secondrow"]//span/@data-tooltip-html').extract()
            url = response.urljoin(href)
            yield scrapy.Request(url, flags=[platforms, rev], callback=self.parse)
    def parse(self, response):
        platforms = response.request.flags[0]
        reviews = response.request.flags[1]
        item = {}
        name = response.xpath('//div[@id="appHubAppName"]/text()').extract()[0] #название
        category = response.xpath('//div[@class="blockbg"]/a/text()').extract()
        del category[0]
        developer = response.xpath('//div[@id="developers_list"]/a/text()').extract()[0] #разработчик
        date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract() #дата выхода
        price = response.xpath('//div[@class="game_purchase_price price"]/text()').extract()[0].strip() #первоначальная цена
        tags = response.xpath('//a[@class="app_tag"]/text()').extract() #теги
        for i in range(len(tags)): #удаляем лишние пробелы в тегах
            tags[i] = tags[i].strip()
        item['name'] = name
        item['category'] = category
        item['reviews'] = reviews
        item['date_of_release'] = date
        item['developer'] = developer
        item['tags'] = tags
        item['price'] = price
        item['platforms'] = platforms
        yield item
