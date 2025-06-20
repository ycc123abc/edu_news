import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "anhui"
    allowed_domains = ["jyt.ah.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = [
                  "https://jyt.ah.gov.cn/content/column/31401481?pageIndex=1",         #通知公告
                   "https://jyt.ah.gov.cn/content/column/31401491?pageIndex=1",           #教育要闻
                   "https://jyt.ah.gov.cn/content/column/31401501?pageIndex=1",              #基础教育
                   "https://jyt.ah.gov.cn/content/column/31401511?pageIndex=1",               #职业教育
                   "https://jyt.ah.gov.cn/content/column/31401521?pageIndex=1",          #高等教育
                      ]
        for url in start_urls:
            wait_ele="//div[@class='rightnr']//li[not(@class='lm_line')]"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"wait_ele":f"xpath:{wait_ele}"})

    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
            item=EduNewsItem()
            item['title']=zixun.xpath("./a[@class='left']/span[@style='color:;']/text()").extract_first()
            item['time']=zixun.xpath("./span/text()").extract_first()
            item['source_web_name']="安徽省教育厅"
            patrurl=urljoin(response.url,zixun.xpath("./a/@href").extract_first())
            item['url']=patrurl
            item['source_url']=response.url
            item['source_name']=response.xpath("//div[@class='wz_top wza-region_nav']/span/a[3]/text()").extract_first()
            current_time=time.localtime()
            item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            yield item
        if current_page==1:
                pages=response.xpath("//a[6]/@paged").extract_first()
                pages = int(pages)
                if pages >= 5:
                    pages = 5
                for next_page in range(2, pages):
                    next_url = urljoin(response.url, f"?pageIndex={next_page}")
                    yield scrapy.Request(url=next_url, callback=self.parse,meta={"page":1,"wait_ele":f"xpath:{wait_ele}"})


        






            

                   


