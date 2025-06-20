import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "jilin"
    allowed_domains = ["jyt.jl.gov.cn"]
    global_page_num:dict={}


    def start_requests(self):
        start_urls = ["http://jyt.jl.gov.cn/zwgk/zcjd/",   #政策解读
                  "http://jyt.jl.gov.cn/zwgk/ggl/",         #公告栏
                   "http://jyt.jl.gov.cn/zwgk/wjtz/zyjy/",           #职业教育文件通知
                   "http://jyt.jl.gov.cn/zyhd/",              #重要活动
                   "http://jyt.jl.gov.cn/jydt/xdt/index.htm",   #各地各高校动态
                   "http://jyt.jl.gov.cn/jydt/gjssdt/",  #国家省级动态
                   "http://jyt.jl.gov.cn/zwgk/wjtz/gdjy/",  #高等教育文件通知


    
        ]
        for url in start_urls:
            print(url)

            self.wait_ele="//table[@class='table1 navBlock']/tbody/tr/td/table[2]/tbody/tr/td[1]/table[1]/tbody/tr"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    


            
    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)

        for zixun in zixuns:

                item=EduNewsItem()
                item['title']=zixun.xpath("./td[1]/a[@class='style_ys03']/text()")[0].extract()
                
                item['time']=zixun.xpath("./td[2]/text()")[0].extract()
                item['source_web_name']="吉林省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./td[1]/a[@class='style_ys03']/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                item['source_name']=response.xpath("//a[@class='CurrChnlCls']/text()")[-1].extract()
   
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item



        if current_page==1 :   
            pages=response.xpath("//div[@id='pages']/a[3]")[0].extract()
            pages=pages.split("_")[-1].split(".")[0]
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"index_{next_page-1}.htm")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})






            

                   


