import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "hebei"
    allowed_domains = ["jyt.hebei.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["http://jyt.hebei.gov.cn/column.jsp?id=1413039313231&current=1",   #全国教育要闻
                  "http://jyt.hebei.gov.cn/column.jsp?id=1405610764482&current=1",         #河北教育要闻
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            wait_ele="//div[@class='col-name']/div/table/tbody/tr"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})



    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./td[1]/a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./td[2]/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")

                item['source_name']=zixun.xpath("//div[@class='col-name'][1]/div/div/text()")[-1].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="河北省教育厅"
                patrurl=zixun.xpath("./td[1]/a/@href")[0].extract()
                item['url']=urljoin(response.url, patrurl)
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            
        if current_page==1:     
            pages=response.xpath("//a[@title='最后页']/@onclick")[0].extract()
            pages=pages.split("(")[-1].split(",")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            for next_page in range(2, pages):
                next_url=response.url.replace(f"current={current_page}", f"current={next_page}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})






            

                   


