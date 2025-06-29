import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "shandong"
    allowed_domains = ["edu.shandong.gov.cn"]

    def start_requests(self):
        start_urls = ["http://edu.shandong.gov.cn/col/col11969/index.html",   # 工作动态
                  "http://edu.shandong.gov.cn/col/col11972/index.html",         #战线联播
                   "http://edu.shandong.gov.cn/col/col11973/index.html",           #新闻发布会
                   "http://edu.shandong.gov.cn/col/col11974/index.html",  #厅长办公会
                   "http://edu.shandong.gov.cn/col/col11975/index.html", #媒体聚焦
                   "http://edu.shandong.gov.cn/col/col278347/index.html", #政策解读
                   "http://edu.shandong.gov.cn/col/col124275/index.html",# 鲁教发
                   "http://edu.shandong.gov.cn/col/col124276/index.html",#鲁教字
                   "http://edu.shandong.gov.cn/col/col124277/index.html",# 鲁教函
                   "http://edu.shandong.gov.cn/col/col11990/index.html",#政策文件
                   "http://edu.shandong.gov.cn/col/col11992/index.html" ,#政策解读
                   "http://edu.shandong.gov.cn/col/col11982/index.html", #通知公告
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="山东省教育厅"
            self.wait_ele="//div[@class='default_pgContainer']/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    


        

    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                
                item['time']=zixun.xpath("./span/text()")[0].extract()
            
                item['source_web_name']=self.source_web_name
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                source_name=response.xpath("//div[@class='dqwz_box']/table/tbody/tr/td[2]/table/tbody/tr/td/a/text()")

                item['source_name']=source_name[-1].extract()

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
                next_url = urljoin(response.url, f"?uid=686126&pageNum={next_page}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})






            

                   


