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


class YoukuFilmItem(scrapy.Item):
    id = scrapy.Field()
    link = scrapy.Field()

    title = scrapy.Field()
    otherTitle = scrapy.Field()

    actors = scrapy.Field()
    director = scrapy.Field()
    genre = scrapy.Field()
    date = scrapy.Field()
    length = scrapy.Field()
    description = scrapy.Field()
    region = scrapy.Field()

    rating = scrapy.Field()
    playCount = scrapy.Field()
    likeCount = scrapy.Field()
    commentCount = scrapy.Field()

    imageURL = scrapy.Field()
    videoURL = scrapy.Field()
