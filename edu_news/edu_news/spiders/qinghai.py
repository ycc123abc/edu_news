import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "qinghai"
    allowed_domains = ["jyt.qinghai.gov.cn"]


    def start_requests(self):
        start_urls = ["https://jyt.qinghai.gov.cn/xw/jydt/",  #教育动态
                      "https://jyt.qinghai.gov.cn/xw/zwyw/",  #政务要闻
                    "https://jyt.qinghai.gov.cn/gk/tzgg/",  #通知公告
                    "https://jyt.qinghai.gov.cn/gk/wsgs/", #网上公示
        ]

        for url in start_urls:
            self.source_web_name="青海省教育厅"
            self.wait_ele="//ul[@id='idul']/li[5]"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    

    def parse(self, response):
        print(response.url,"开始爬虫")
        zixuns=response.xpath("//ul[@id='idul']/li")
        for zixun in zixuns:
            item=EduNewsItem()
            item['title']=zixun.xpath("./a/text()")[0].extract()
            item['time']=zixun.xpath("./span/text()")[0].extract()
            item['source_web_name']=self.source_web_name
            patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
            item['url']=patrurl
            item['source_url']=response.url
            source_name=response.xpath("//div[@id='r1']/p[1]/a/text()")
            item['source_name']=source_name[0].extract()
            current_time=time.localtime()
            item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)

            yield item
 






            

                   


