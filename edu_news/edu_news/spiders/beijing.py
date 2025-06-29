import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
class ZygovSpider(scrapy.Spider):
    name = "beijing"
    allowed_domains = ["jw.beijing.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["https://jw.beijing.gov.cn/jyzx/jyxw/",   #教育新闻
                  "https://jw.beijing.gov.cn/jyzx/spxw/",         #视频新闻
                  "https://jw.beijing.gov.cn/xxgk/zxxxgk/",            #最新信息公开
                   "https://jw.beijing.gov.cn/xxgk/2024zcjd/",           #政策解读
                   "https://jw.beijing.gov.cn/xxgk/2024zcwj/2024xzgfwj/",      #行政规范性文件
    
        ]
        for url in start_urls:
            print(url)
            wait_ele="//div[@class='announce_list a-hov-c']/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"wait_ele":f"xpath:{wait_ele}"})
                                 
    def parse(self, response):
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()").extract_first()
                item['time']=zixun.xpath("./span/text()").extract_first()
                item['source_web_name']="北京市教育委员会"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                item['source_name']=zixun.xpath("//a[@class='CurrChnlCls'][3]/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item


        if current_page==1:
                pages=response.selector.re_first(r'countPage = (\d+)')
                pages = int(pages)
                if pages >= 5:
                    pages = 5
                for next_page in range(2, pages):
                    next_url = urljoin(response.url, f"index_{next_page-1}.html")
                    yield scrapy.Request(next_url, callback=self.parse,meta={"page":1,"wait_ele":f"xpath:{wait_ele}"})






            

                   


