import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "ningxia"
    allowed_domains = ["jyt.nx.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["https://jyt.nx.gov.cn/xwdt/tzgg/index.html",   #通知公告
                  "https://jyt.nx.gov.cn/xwdt/zdhy/index.html",         #重要会议
                   "https://jyt.nx.gov.cn/xwdt/gzdt/index.html",           #工作动态
                   "https://jyt.nx.gov.cn/zwgk/zcwj/zzqzfwj/index.html",              #自治区文件
    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            if "zcwj" not in url:
                wait_ele="//ul[@class='wzlb']/a"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//div[@class='zfxxgk_zd1']"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})


            

    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                if "zcwj" not in response.url:
                    item['title']=zixun.xpath("./li/p/text()")[0].extract()
                    item["time"]=zixun.xpath("./li/span/text()")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    item['source_name']=zixun.xpath("//p[@class='qdwz']/text()[2]")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    patrurl=urljoin(response.url,zixun.xpath("./@href")[0].extract())
                    item['url']=patrurl
                else:
                    item['title']=zixun.xpath("./a/text()")[0].extract()
                    item["time"]=zixun.xpath("./b/text()")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    item['source_name']=zixun.xpath("//div[@class='zfxxgk_zdgktit']/a/text()")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                    item['url']=patrurl
                item['source_web_name']="宁夏省教育厅"
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item


        if current_page==1 :   
            try:
                pages=response.xpath("//a[@class='be']/@href")[0].extract()
                pages=pages.split("_")[-1].split(".")[0].replace(" ","")
            except:
                pages=response.xpath("//a[7]/text()")[0].extract()
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})






            

                   


