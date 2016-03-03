# -*- coding: utf-8 -*-
import scrapy

from movies.items import YoukuFilmItem
from movies.output import writeln, color


class YoukuListSpider(scrapy.Spider):
    name = "youku"
    allowed_domains = ["youku.com"]

    def __init__(self, **kwargs):
        super(YoukuListSpider, self).__init__(**kwargs)
        self.start_urls = ['http://www.youku.com/v_olist/c_96.html']

    def parse(self, response):
        writeln('[' + color('SPIDER', 'blue') + '] Parsing link: ' + response.url)

        films = response.xpath('//div[@id="listofficial"]/descendant::div[contains(@class, "yk-col3")]')
        for film in films:
            item = YoukuFilmItem()
            item['link'] = response.urljoin(film.xpath('div/div[contains(@class, "p-link")]/a/@href')[0].extract())
            request = scrapy.Request(item['link'], self.parse_movie)
            request.meta['item'] = item
            yield request

        next_page = response.xpath('//ul[@class="yk-pages"]/li[@class="next"]/a/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)

    def parse_movie(self, response):
        item = response.meta['item']
        info = response.xpath('//div[contains(@class, "showInfo")]')

        def extract(attrib, xpath):
            result = info.xpath('descendant::' + xpath).extract()
            if result:
                item[attrib] = map(lambda x: x.strip(), result)

        item['title'] = response.xpath('//h1[@class="title"]/span[@class="name"]/text()')[0].extract()
        alias = info.xpath('descendant::span[@class="alias"]/@title')
        if alias:
            item['otherTitle'] = alias[0].extract().split('/')

        extract('actors', 'span[@class="actor"]/a/text()')
        extract('director', 'span[@class="director"]/a/text()')
        extract('genre', 'span[@class="type"]/a/text()')
        extract('date', 'span[@class="pub"][1]/text()')
        extract('length', 'span[@class="duration"]/text()')
        extract('region', 'span[@class="area"]/a/text()')
        desc = response.xpath('//div[contains(@class, "detail")]/span[@class="long"]/text()').extract()
        if not desc:
            desc = response.xpath('//div[contains(@class, "detail")]/span[@class="short"]/text()').extract()
        item['description'] = ''.join(map(lambda x: x.strip(), desc))

        rate = info.xpath('descendant::li[contains(@class, "rate")]/span/span/em[@class="num"]/text()')
        if rate:
            item['rating'] = float(rate[0].extract())
        extract('playCount', 'span[@class="play"]/text()')
        extract('commentCount', 'span[@class="comment"]/em/text()')
        extract('likeCount', 'span[@class="increm"]/text()')

        item['imageURL'] = info.xpath('descendant::li[@class="thumb"]/img/@src')[0].extract()

        button = response.xpath('//ul[@class="baseaction"]/li/a[contains(@class, "btnfreesee")]')
        if not button:
            button = response.xpath('//ul[@class="baseaction"]/li/a[contains(@class, "btnplayposi")]')
        if button:
            item['videoURL'] = button.xpath('@href')[0].extract()
        else:
            writeln('[' + color('IGNORE', 'magenta') + '] ' + item['title'] + ' has no video link')

        yield item
