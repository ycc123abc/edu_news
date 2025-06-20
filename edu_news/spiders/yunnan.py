import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "yunnan"
    allowed_domains = ["jyt.yn.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["https://jyt.yn.gov.cn/article/category/38d5f8d6af024bd0abe28cc484b18af0-1",   #教育信息
                  "https://jyt.yn.gov.cn/article/category/b99635e859f74b70b0d855812d7452fc-1",         #政策文件
                   "https://jyt.yn.gov.cn/article/category/fb23c6e425a14040a8efbef2fa58e43f-1",           #公式公告
                   "https://jyt.yn.gov.cn/article/category/4bd1bac5820642cfb7e2cf7af02f1484-1",              #政策解读
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            if "38d5f8d6af024bd0abe28cc484b18af0" in url:
                wait_ele="//div[@class='jyxxlb']/div[2]/div[@class='jyxxnr1']"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//div[@class='yemian']/ul[1]/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})


            



    def parse(self, response):
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                if  "38d5f8d6af024bd0abe28cc484b18af0" in response.url:
                    item['source_name']="教育信息"
                else:
                    item['source_name']=response.xpath("//title/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="云南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            


        if current_page==1 :   
            pages=response.xpath("//span[contains(text(), '条记录')]/text()")[0].extract()
            pages=pages.split("/")[-1].split("页")[0].replace(" ","")
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=response.url.split("-")[0]+f"-{next_page}"
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":f"xpath:{wait_ele}"})





            

                   


