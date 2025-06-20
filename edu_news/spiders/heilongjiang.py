import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import json
class ZygovSpider(scrapy.Spider):
    name = "heilongjiang"
    allowed_domains = ["jyt.hlj.gov.cn"]

    def start_requests(self):
        start_urls = ["http://jyt.hlj.gov.cn/common/search/d9459b0a5b814070974bee87b113b6a1?_isAgg=true&_isJson=true&_pageSize=15&_template=index&_rangeTimeGte=&_channelName=&page=1",   #教育厅
                   "http://jyt.hlj.gov.cn/common/search/bffa5a0ba13c428bb95799f87aa2e9fe?_isAgg=true&_isJson=true&_pageSize=15&_template=index&_rangeTimeGte=&_channelName=&page=1",           #通知公告
                   "http://jyt.hlj.gov.cn/common/search/443c0ba9d1a74f709497959900a6025e?_isAgg=true&_isJson=true&_pageSize=15&_template=index&_rangeTimeGte=&_channelName=&page=1",          #市县区
                   "http://jyt.hlj.gov.cn/common/search/e575055b2b3f4ef2ba1ee5c53e36475a?_isAgg=true&_isJson=true&_pageSize=15&_template=index&_rangeTimeGte=&_channelName=&page=1"          #学校
        ]

        for url in start_urls:
            if "e575055b2b3f4ef2ba1ee5c53e36475a" in url:
                # for i in range(1, 131):
                for i in range(1, 5):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"json": True,"change":True})

            if "d9459b0a5b814070974bee87b113b6a1" in url:
                # for i in range(1, 156):
                for i in range(1, 5):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"json": True,"change":True})

            if "bffa5a0ba13c428bb95799f87aa2e9fe" in url:
                # for i in range(1, 71):
                for i in range(1, 5):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"json": True,"change":True})
            
            if "443c0ba9d1a74f709497959900a6025e" in url:
                # for i in range(1, 95):
                for i in range(1, 5):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"json": True,"change":True})




    def parse(self, response):
        response_json  =  json.loads(response.text)
        results = response_json["data"]["results"]
        for result in results:
            item=EduNewsItem()
            item["title"]=result["title"]
            item["url"]=urljoin(response.url,result["url"])
            item["time"]=result["publishedTimeStr"]
            current_time=time.localtime()
            item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            item['source_url']=response.url
            item['source_web_name']="黑龙江省教育厅"
            item['source_name']=result["channelName"]


            yield item
            







            

                   


