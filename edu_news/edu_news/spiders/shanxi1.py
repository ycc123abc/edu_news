import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "shaanxi"
    allowed_domains = ["jyt.shaanxi.gov.cn"]
    global_page_num:dict={}


    def start_requests(self):
        start_urls = ["https://jyt.shaanxi.gov.cn/index/tt/",   #  头条推荐
                  "https://jyt.shaanxi.gov.cn/index/dtyw/",         # 教育要闻
                   "https://jyt.shaanxi.gov.cn/index/dsyw/",           # 战线联播
                   "https://jyt.shaanxi.gov.cn/index/mtr/",   # 媒体视角
                   "https://jyt.shaanxi.gov.cn/gk/fdnr/gsgggk/"  #公示公告
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="陕西省教育厅"
            self.global_page_num[url]=None
            if "fdnr" not in url:
                self.wait_ele="//li[@class='clearfix']"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
            else:
                self.wait_ele="//ul[@class='cm-news-list']/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                item['source_web_name']=self.source_web_name
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                if "fdnr" not in response.url:
                    item['source_name']=response.xpath("//li[@class='active cur']/text()")[0].extract()
                    item["time"]=zixun.xpath("./span/text()")[0].extract()
                else:
                    item["time"]=zixun.xpath("./span[@class='con-times']/text()")[0].extract()
                    item["time"]=zixun.xpath("./span/text()")[0].extract()
                    item['source_name']="公示公告"
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item

            

        if current_page==1 :   
            pages=response.xpath("//div[@id='page']/span/text()")[0].extract()
            pages=pages.split("/")[-1].split("页")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})




            

                   


