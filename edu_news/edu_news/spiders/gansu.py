import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import json
from lxml import etree
class ZygovSpider(scrapy.Spider):
    name = "gansu"
    allowed_domains = ["jyt.gansu.gov.cn"]

    def start_requests(self):
        start_urls = [
            "https://jyt.gansu.gov.cn",
            "https://jyt.gansu.gov.cn/common/search/6ed9cac952e94022bd5bd213764b983d?sort=&_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_rangeTimeLt=&_channelName=&page=1",   #媒体聚焦
                   "https://jyt.gansu.gov.cn/common/search/c7df0c0ea0b7444d9744d4a6c1fcca4b?sort=&_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_rangeTimeLt=&_channelName=&page=1",           #教育动态
                   "https://jyt.gansu.gov.cn/common/search/695dc7247ea148ad8e01ad5988132d63?sort=&_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_rangeTimeLt=&_channelName=&page=1",          #教育要闻

                 
        ]
        for url in start_urls:
            if "6ed9cac952e94022bd5bd213764b983d" in url:
                # for i in range(1, 232):
                for i in range(1, 10):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"num":2})

            elif "c7df0c0ea0b7444d9744d4a6c1fcca4b" in url:
                # for i in range(1, 530):
                for i in range(1, 10):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"num":2})

            elif "695dc7247ea148ad8e01ad5988132d63" in url:
                # for i in range(1, 211):
                for i in range(1, 10):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,meta={"num":2})
            
            else:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        if response.url=="https://jyt.gansu.gov.cn/":
            pass
        else:
            json_text=response.xpath('//pre/text()')[0].extract()
            response_json  =  json.loads(json_text)
            results = response_json["data"]["results"]
            for result in results:
                item=EduNewsItem()
                item["title"]=result["title"]
                item["url"]=urljoin(response.url,result["url"])
                item["time"]=result["publishedTimeStr"]
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                item['source_url']=response.url
                item['source_web_name']="甘肃省教育厅"
                item['source_name']=result["channelName"]


                yield item
                







                

                    


