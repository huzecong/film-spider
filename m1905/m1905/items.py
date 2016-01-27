# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class M1905FilmItem(scrapy.Item):
    id = scrapy.Field()
    link = scrapy.Field()

    title = scrapy.Field()
    titleEng = scrapy.Field()

    actors = scrapy.Field()
    director = scrapy.Field()
    boxOffice = scrapy.Field()
    genre = scrapy.Field()
    date = scrapy.Field()
    awards = scrapy.Field()

    tags = scrapy.Field()

    imageURL = scrapy.Field()
    videoURL = scrapy.Field()
