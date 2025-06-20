import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "hainan"
    allowed_domains = ["edu.hainan.gov.cn"]



    def start_requests(self):
        start_urls = [
      
                #    "http://edu.hainan.gov.cn/common/search/459d0a8a28674196bc67bbfa4db378a8?sort=publishedTime&_isAgg=false&_isJson=false&_pageSize=12&_template=edu&_rangeTimeGte=&_channelName=&page=1",          #公示公告
                   "http://edu.hainan.gov.cn/edu/zxjd/tylist.shtml",      #最新解读
        ]
        for url in start_urls:
            if "common" in url:
                wait_ele_1="//div[@class='cen-div-1 mar-t']/div"
                yield scrapy.Request(url=url, callback=self.first_parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele_1}"})
            else:
                wait_ele_2="//dl/li"
                yield scrapy.Request(url=url, callback=self.second_parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele_2}"})

    
    def first_parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        
        for zixun in zixuns[:-1]:
                item=EduNewsItem()
                item['title']=zixun.xpath("./div[@class='list-right_title fon_1']/a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./table/tbody/tr/td[1]/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","").replace("发布时间：","")
                item['source_name']=(zixun.xpath("//div[@class='list_left_title']/text()"))[0].extract().replace(" ","").replace("\n","").replace("\t","")



                item['source_web_name']="海南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./div[@class='list-right_title fon_1']/a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item


        if current_page==1:     
            pages=response.xpath("//a[contains(text(), '末页')]/@href")[0].extract()
            pages=pages.split("=")[-1]
            pages=int(pages) 
            if pages >= 5:
                pages = 5
            for next_page in range(2, pages):
                next_url=response.url[:-1]+str(next_page)
                yield scrapy.Request(next_url, callback=self.first_parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})

            
    def second_parse(self, response):
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./em/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","").replace("发布时间：","")
                item['source_name']=(zixun.xpath("//ul[@class='htm_zb-01']/h2/text()"))[0].extract().replace(" ","").replace("\n","").replace("\t","")

                item['source_web_name']="海南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            

        if current_page==1:     
            pages=response.xpath("//a[contains(text(), '末页')]/@href")[0].extract()
            pages=pages.split("_")[-1].split(".")[0]
            pages=int(pages) 
            if pages >= 5:
                pages = 5
            for next_page in range(2, pages):
                next_url=urljoin(response.url,f"tylist_{next_page}.shtml")
                yield scrapy.Request(next_url, callback=self.first_parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})
                   


