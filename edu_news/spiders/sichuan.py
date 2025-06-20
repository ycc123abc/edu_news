import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "sichuan"
    allowed_domains = ["edu.sc.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["http://edu.sc.gov.cn/scedu/c100494/xwzx_list.shtml",   #委厅信息
                  "http://edu.sc.gov.cn/scedu/c100495/xwzx_list.shtml",         #通知公告
                   "http://edu.sc.gov.cn/scedu/c100496/xwzx_list.shtml",           #视频新闻
                   "http://edu.sc.gov.cn/scedu/c100498/xwzx_list.shtml",              #市州区县动态
                   "http://edu.sc.gov.cn/scedu/c100499/xwzx_list.shtml",        #高等学校动态
                   "http://edu.sc.gov.cn/scedu/c100500/xwzx_list.shtml",          #基层学校动态
                   "http://edu.sc.gov.cn/scedu/c100507/xwzx_list.shtml",      #网信工作
                   "http://edu.sc.gov.cn/scedu/c100503/xwzx_list.shtml",          #政策解读
                   "http://edu.sc.gov.cn/scedu/c100505/xwzx_list.shtml",          #招考录用
    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None

            wait_ele="//ul[@class='xwzxList']/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})




    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_name']=zixun.xpath("//div[@class='title']/span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="四川省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item


        if current_page==1 :   
            pages=response.xpath("//a[@class='pagination-index'][4]/@href")[0].extract()
            pages=pages.split("_")[-1].split(".")[0].replace(" ","")
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=urljoin(response.url,f"xwzx_list_{next_page}.shtml")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})





            

                   


