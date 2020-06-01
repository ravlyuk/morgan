# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    url = scrapy.Field()
    photo = scrapy.Field()
    name = scrapy.Field()
    position = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    services = scrapy.Field()
    sectors = scrapy.Field()
    publications = scrapy.Field()
    brief = scrapy.Field()
    datetime = scrapy.Field()
