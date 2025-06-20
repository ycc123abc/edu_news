import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback

"""
含有ajax 
"""
class ZygovSpider(scrapy.Spider):
    name = "xizang"
    allowed_domains = ["edu.xizang.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["http://edu.xizang.gov.cn/7/20/index.html",   #教育要闻
                  "http://edu.xizang.gov.cn/7/21/index.html",         #政策解读
                #    "http://edu.xizang.gov.cn/6/index.html",           #公式公告
                #    "http://edu.xizang.gov.cn/6/index.html",              #文件通知
    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            if "7" in url:
                wait_ele="//div[@class='content-box']/ul/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//div[@class='notice']/ul/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})


    def parse(self, response):

        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
 
                item['source_name']=response.xpath("//p[@class='inline-block']/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","").replace(" ","").replace("\n","").replace(">","")
                item['source_web_name']="西藏省教育厅"
                patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item

            
        if current_page==1 :   
            pages=response.xpath("//a[@class='last']/@href")[0].extract()
            pages=pages.split("list")[-1].split(".")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=urljoin(response.url, f"list{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":f"xpath:{wait_ele}"})

        



            

                   


