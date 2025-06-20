import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "jiangsu"
    allowed_domains = ["jyt.jiangsu.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["https://jyt.jiangsu.gov.cn/col/col82269/index.html?uid=396302&pageNum=1",   #时政要闻
                  "https://jyt.jiangsu.gov.cn/col/col57807/index.html",         #教育要闻
                  "https://jyt.jiangsu.gov.cn/col/col58320/index.html",            #通知公告
                   "https://jyt.jiangsu.gov.cn/col/col57812/index.html",           #市县动态
                   "https://jyt.jiangsu.gov.cn/col/col57813/index.html",      #高校动态
                   "https://jyt.jiangsu.gov.cn/col/col57810/index.html",            #媒体聚焦
                   "https://jyt.jiangsu.gov.cn/col/col57816/index.html"  ,             #图片新闻

    
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://div[@class='default_pgContainer']/li[@class='cf']"})



    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        zixuns=response.xpath("//div[@class='default_pgContainer']/li[@class='cf']")
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                item['time']=zixun.xpath("./span[@class='fr']/text()")[0].extract()
                item['source_web_name']="江苏省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                item['source_name']=zixun.xpath("//div[@class='currentPosition']/table/tbody/tr/td[3]/table/tbody/tr/td[2]/a/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item

        if current_page==1 :   
            pages=response.xpath("//span[@class='default_pgTotalPage']/text()")[0].extract()
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"?uid=396302&pageNum={next_page}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":"xpath://div[@class='default_pgContainer']/li[@class='cf']"})






                

# Compare this snippet from edu_news/spiders/guangdong.py: 


