import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "hunan"
    allowed_domains = ["jyt.hunan.gov.cn"]
    global_page_num:dict={}
    
    wait_ele=None
    def start_requests(self):
        start_urls = ["https://jyt.hunan.gov.cn/jyt/sjyt/jyyw/2019_zfxxgk_listsub.html",             #教育要闻
                  "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/jykx/jykx_1/index.html",               #教育快讯
                  "https://jyt.hunan.gov.cn/jyt/sjyt/bwdt/index.html",                    #部委动态
                   "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/szdt/index.html",           #一线采风 市州动态
                   "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/gxdt/index.html",                #一线采风 高校动态
                #    "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/c100959/index.html",         #文件库
                "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/tzgg/index.html",                 #通知公告
                "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/zcfg/zcjd/index.html"             #政策解读

    
        ]
        for url in start_urls:
            self.wait_ele="//ul[@class='list_gkzd_content']/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    


            
    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        zixuns=response.xpath("//ul[@class='list_gkzd_content']/li")

        for zixun in zixuns:

                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                item['time']=zixun.xpath("./span/text()")[0].extract()
                item['source_web_name']="湖南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                if "jyyw" in response.url:
                    item['source_name']="教育要闻"
                elif "xxgk" in response.url:
                    item['source_name']="教育快讯"
                elif "bwdt" in response.url:
                    item['source_name']="部委动态"
                elif "szdt" in response.url:
                    item['source_name']="一线采风 市州动态"
                elif "gxdt" in response.url:
                    item['source_name']="一线采风 高校动态"
                elif "tzgg" in response.url:
                    item['source_name']="通知公告"
                elif "zcfg" in response.url:
                    item['source_name']="政策解读"

                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item

            


        if current_page==1 :   
            if "bwdt" in response.url:
                return
            pages=response.xpath("//li[@class='end_page']/a/@href")[0].extract()
            pages=pages.split("_")[-1].split(".")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"index_{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":f"xpath:{self.wait_ele}"})






            

                   


