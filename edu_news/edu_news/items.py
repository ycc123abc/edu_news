# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EduNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    source_web_name= scrapy.Field()    #来源网站
    source_name= scrapy.Field()    #来源板块
    source_url= scrapy.Field()     
    title  = scrapy.Field()
    url= scrapy.Field()
    time   = scrapy.Field()
    create_time= scrapy.Field()
