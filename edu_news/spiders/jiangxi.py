import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "jiangxi"
    allowed_domains = ["jyt.jiangxi.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = [
                  "http://jyt.jiangxi.gov.cn/jxjyw/tzgg785/index.html",         #通知公告
                   "http://jyt.jiangxi.gov.cn/jxjyw/sjyt/index.html",           #省教育厅
                   "http://jyt.jiangxi.gov.cn/jxjyw/jyb877/pc/list.html",              #政策文件
        ]
        for url in start_urls:
            self.wait_ele="//div[@class='default_pgContainer']/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    
    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a[@class='b-free-read-leaf']/text()")[0].extract()
                
                item['time']=zixun.xpath("./span[@class='b-free-read-leaf']/text()")[0].extract()
                item['source_web_name']="江西省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a[@class='b-free-read-leaf']/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                item['source_name']=response.xpath("//div[@class='title_name b-free-read-leaf']/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            
        if current_page==1 :   
            pages=response.xpath("//span[@class='default_pgTotalPage']/text()")[0].extract()
            pages=pages.split("_")[-1].split(".")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"?uid=368486&pageNum={next_page}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":f"xpath:{wait_ele}"})






            

                   


