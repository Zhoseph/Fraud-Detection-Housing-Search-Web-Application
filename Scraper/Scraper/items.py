# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ListingItem(scrapy.Item):
    website = scrapy.Field()
    pid = scrapy.Field()
    repostId = scrapy.Field()
    dt = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    bedroom = scrapy.Field()
    area = scrapy.Field()
    hood = scrapy.Field()
    agent = scrapy.Field()
    accuracy = scrapy.Field()
    address = scrapy.Field()
    isFlagged =  scrapy.Field()
    isRemoved =  scrapy.Field()
    description = scrapy.Field()
    image =  scrapy.Field()
    listid = scrapy.Field()
    contact = scrapy.Field()
    pass
