import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "henan"
    allowed_domains = ["jyt.henan.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["https://jyt.henan.gov.cn/jydt/zscd/",   # 政声传递
                  "https://jyt.henan.gov.cn/jydt/yjyw/",         #豫教要闻
                   "https://jyt.henan.gov.cn/jydt/mtjj/",           #媒体聚焦
                   "https://jyt.henan.gov.cn/jydt/gxdt/",    #高校动态
                   "https://jyt.henan.gov.cn/jydt/sxdt/",  #市县动态
                   "https://jyt.henan.gov.cn/jydt/xwfb/", #新闻发布
                   "https://jyt.henan.gov.cn/jydt/zcjd/", #政策解读



    
        ]
        for url in start_urls:
            print(url)
            self.source_web_name="河南省教育厅"
            self.global_page_num[url]=None
            self.wait_ele="//div[@class='list']/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    


            



    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)

        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                
                item['time']=zixun.xpath("./span/text()")[0].extract()
                
                item['source_web_name']=self.source_web_name
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                item['source_name']=response.xpath("//div[@class='subnav']/a[3]/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except:
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            


        if current_page==1:     
            pages=response.xpath("//span[@class='sDisable'][4]/@data-page")[0].extract()
            pages=int(pages)
            if pages >= 5:
                pages = 5
            for next_page in range(2, pages ):
                next_url = urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":f"xpath:{wait_ele}"})






            

                   


