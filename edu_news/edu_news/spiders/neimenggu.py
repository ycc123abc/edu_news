import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "neimenggu"
    allowed_domains = ["jyt.nmg.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["https://jyt.nmg.gov.cn/jydt/zhxx/",   #  综合信息
                        "https://jyt.nmg.gov.cn/jydt/bjjy/",     #北疆教育
                  "https://jyt.nmg.gov.cn/zwgk/tzgg_25132/",         # 通知公告
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="内蒙古省教育厅"
            self.wait_ele="//div[contains(@class,'tygl_con_con')]/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,'wait_ele':f"xpath:{self.wait_ele}"})


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()

                item['title']=zixun.xpath("./a/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                item['time']=zixun.xpath("./span/text()")[-1].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                item['source_name']=response.xpath("//div[@class='tygl_con_tit']/span/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract())
                item['url']=patrurl
                item['source_web_name']=self.source_web_name
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item



        if current_page==1 :   
            pages=response.xpath("//div[@class='xll_pagebox']/span[1]/font/text()")[0].extract()
            pages=pages.split("共")[-1].split("页")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,'wait_ele':f"{self.wait_ele}","change":True})






            

                   


