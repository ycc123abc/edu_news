import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "xinjiang"
    allowed_domains = ["jyt.xinjiang.gov.cn"]
    global_page_num:dict={}


    def start_requests(self):
        start_urls = ["https://jyt.xinjiang.gov.cn/edu/jydt/list_xw.shtml",   #教育动态
                  "https://jyt.xinjiang.gov.cn/edu/jiaoyudt/list_xw.shtml",         #工作动态
                   "https://jyt.xinjiang.gov.cn/edu/xuexiaodt/list_xw.shtml",           #学校动态
                   "https://jyt.xinjiang.gov.cn/edu/dzdt/list_xw.shtml",              #地州动态
                   "https://jyt.xinjiang.gov.cn/edu/gsgg/list_xw.shtml",        #公示公告
                   "https://jyt.xinjiang.gov.cn/edu/fbh/list_xw.shtml",          #发布会
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None

            wait_ele="//div[@class='tab']/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})



    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")

                item["time"]=zixun.xpath("./div/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","").replace("(","").replace(")","")
                item['source_name']=zixun.xpath("//div[@class='mbx']/p/span/text()")[-1].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="新疆省教育厅"
                patrurl=zixun.xpath("./a/@href")[0].extract()
                item['url']=urljoin(response.url,patrurl)
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            

        if current_page==1 :   
            pages=response.xpath("//a[@class='pagination-index'][4]/@href")[0].extract()
            pages=pages.split("_")[-1].split(".")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=urljoin(response.url,f"list_xw_{next_page}.shtml")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":f"xpath:{wait_ele}"})




            

                   


