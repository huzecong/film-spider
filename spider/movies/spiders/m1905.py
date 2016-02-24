# -*- coding: utf-8 -*-
import scrapy
import subprocess
import urllib

from movies.items import M1905FilmItem


class M1905Spider(scrapy.Spider):
    name = "m1905"
    allowed_domains = ["1905.com"]

    def __init__(self, **kwargs):
        super(M1905ListSpider, self).__init__(**kwargs)
        # total_movies = 316770
        total_movies = 300
        movies_per_page = 30
        total_pages = (total_movies + movies_per_page - 1) // movies_per_page
        self.start_urls = [("http://www.1905.com/mdb/film/list/o0d0p%d.html" % x) for x in xrange(1, total_pages + 1)]
        # self.start_urls = [("http://www.1905.com/mdb/film/list/o0d1p%d.html" % x) for x in xrange(1, total_pages + 1)]

    def handler(self, request):
        print request.url

    def parse(self, response):
        print "Parsing url:", response.url

        films = response.xpath('//ul[contains(@class, "inqList")]/li[contains(@class, "fl")]')
        for film in films:
            item = M1905FilmItem()
            item['link'] = response.urljoin(film.xpath('div/p[1]/a/@href')[0].extract())
            request = scrapy.Request(item['link'], self.parse_movie)
            request.meta['item'] = item
            yield request

        '''
        next_page = response.xpath(u'//a[text()="下一页"]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)
        '''

    def parse_movie(self, response):
        item = response.meta['item']
        name = response.xpath('//div[contains(@class, "laMovName")]')
        item['title'] = name.xpath('h1/a/text()')[0].extract()
        name_eng = name.xpath('div/span[1]/a/text()')
        if name_eng:
            item['titleEng'] = name_eng[0].extract().strip()
        staff = response.xpath('//ol[contains(@class, "movStaff")]')

        def extract(name):
            parent_path = u'descendant::strong[contains(text(), "%s")]/parent::*/' % name
            child_path = u'descendant::a[contains(@class, "laBlueS_f")]/text()'
            elem = staff.xpath(parent_path + child_path)
            if not elem:
                child_path = u'descendant::a[contains(@class, "maintag")]/text()'
                elem = staff.xpath(parent_path + child_path)
            if elem:
                values = map(lambda x: x.strip(), elem.extract())
                return values
            return ''

        def assign(prop, name):
            values = extract(name)
            if values != '':
                if len(values) == 1:
                    item[prop] = values[0]
                else:
                    item[prop] = values

        assign('director', u"导演")
        assign('actors', u"主演")
        assign('genre', u"类型")
        assign('boxOffice', u"票房")
        assign('tags', u"基因")
        date = extract(u"日期")
        if date:
            item['date'] = u"年".join(date)
        awards = filter(lambda x: u"获奖" in x, extract(u"获奖"))
        if awards:
            times = int(filter(lambda x: '0' <= x <= '9', awards[0]))
            item['awards'] = times

        item['imageURL'] = response.xpath('//div[contains(@class, "laMovPIC")]/descendant::img/@src')[0].extract()

        button = response.xpath(u'//ol[contains(@class, "movie-btns")]/'
                                u'li[contains(@class, "redBtn")]/a/p[text()="立即观看"]')
        if button:
            url = button.xpath('parent::*/@href')[0].extract()
            if url.find('http://www.1905.com/vod/play/') != -1:
                item['videoURL'] = url
                yield item
            else:
                yield scrapy.Request(url, self.parse_video_1, meta={'item': item})
        else:
            # print item['title'], "no video"
            yield item

    def parse_video_1(self, response):
        button = response.xpath('//a[contains(@class, "play-video")]')
        if button:
            url = button.xpath('@href')[0].extract().split('?')[0]
            yield scrapy.Request(url, self.parse_video_2, meta=response.meta)
        else:
            # print response.meta['item']['title'], "no video"
            yield response.meta['item']

    def parse_video_2(self, response):
        # video = response.xpath('//span[contains(@class, "videoplay")]/parent::a')
        info = response.xpath('//div[contains(@class, "mi_txt")]')
        if info:
            url = info.xpath('a[last()]/text()')[0].extract().strip()
            # script = video.xpath('@onclick')[0].extract()
            # url = urllib.unquote(script.split('url=')[1].split('&fr=')[0])
            # print response.meta['item']['title'], url
            # subprocess.call(["wget", "-O", response.meta['item']['title'], url])
            yield scrapy.Request(url, self.parse_video_3, meta=response.meta)
        else:
            # print response.meta['item']['title'], "no video"
            yield response.meta['item']

    def parse_video_3(self, response):
        # print response.url
        item = response.meta['item']
        item['videoURL'] = response.url
        yield item
