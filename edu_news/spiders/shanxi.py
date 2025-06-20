import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time


class ZygovSpider(scrapy.Spider):
    name = "shanxi"
    allowed_domains = ["jyt.shanxi.gov.cn"]



    def start_requests(self):
        start_urls = ["https://jyt.shanxi.gov.cn/xwzx/ywsd/",   #  要闻速递
                  "https://jyt.shanxi.gov.cn/xwzx/ggtz/",         # 公告通知
                   "https://jyt.shanxi.gov.cn/xwzx/gzdt/",           # 工作动态
                   "https://jyt.shanxi.gov.cn/xwzx/sxdt/",  # 市校动态
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="山西省教育厅"
            self.wait_ele="//div[@class='xwzx_ggtz']//li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:
                item=EduNewsItem()

                item['title']=zixun.xpath("./a//text()")[0].extract()

                item['time']=zixun.xpath("./span/text()")[0].extract()
                item['source_web_name']=self.source_web_name
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                source_name=response.xpath("//a[@class='CurrChnlCls'][3]/text()")
                item['source_name']=source_name[-1].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            

        if current_page==1 :   
            pages=response.xpath("//div[@class='ye']/a[4]/@href")[0].extract()
            pages=pages.split("_")[-1].split(".")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})






            

                   


