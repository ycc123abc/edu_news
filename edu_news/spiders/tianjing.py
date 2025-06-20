import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "tianjing"
    allowed_domains = ["jy.tj.gov.cn"]
    global_page_num:dict={}


    def start_requests(self):
        start_urls = ["https://jy.tj.gov.cn/ZWGK_52172/TZGG/",   #通知公告
                  "https://jy.tj.gov.cn/ZWGK_52172/zcwj/sjwwj/index.html",         #市教委文件
                   "https://jy.tj.gov.cn/ZWGK_52172/zcjd_1/index.html",           #政策解读
                   "https://jy.tj.gov.cn/JYXW/TJJY/index.html",              #天津教育
                   "https://jy.tj.gov.cn/JYXW/GNJY/index.html",        #国内教育
                   "https://jy.tj.gov.cn/JYXW/JCJY/index.html",          #基层教育
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None

            wait_ele="//ul[@class='common-list-right-list']/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})



    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        has_new = True
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/p[@class='list-content']/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./p[@class='list-date']/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")

                item['source_name']=zixun.xpath("//a[@class='tagcolor']/text()")[-1].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="天津市教育委员会"
                patrurl=zixun.xpath("./a/@onclick")[0].extract()
                patrurl=patrurl.replace("isDownLoad(this,'","").replace("')","")
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            

        
        if current_page==1 and "TZGG" not in response.url:   
            pages=response.xpath("//div[@class='page-list']/span[2]/text()")[0].extract()
            pages=pages.replace("共","").replace("页","")
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=urljoin(response.url,f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})





            

                   


