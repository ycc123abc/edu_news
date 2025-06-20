import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "guizhou"
    allowed_domains = ["jyt.guizhou.gov.cn"]

    def start_requests(self):
        start_urls = [
                   "https://jyt.guizhou.gov.cn/xwzx/szyw/index.html",        #贵州要闻
                   "https://jyt.guizhou.gov.cn/xwzx/gzdt/index.html",          #工作动态
                   "https://jyt.guizhou.gov.cn/xwzx/gzdt/index.html",      #综合信息
                   "https://jyt.guizhou.gov.cn/xwzx/zxlb/index.html",          #战线联播
                   "https://jyt.guizhou.gov.cn/xwzx/tzgg/index.html",          #通知公告
                   "https://jyt.guizhou.gov.cn/ywgz/jsgz/index.html",         #教师工作
                   "https://jyt.guizhou.gov.cn/ywgz/gdjy/index.html",         #高等教育
                   "https://jyt.guizhou.gov.cn/ywgz/zyjy/index.html",          #职业教育
                   "https://jyt.guizhou.gov.cn/ywgz/kxyj/index.html",  #科学研究
        ]
        for url in start_urls:
            print(url)


            wait_ele="//div[@class='NewsList']/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})



        
    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")

        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")

                item['source_name']=zixun.xpath("//h1/span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="贵州省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item



        if current_page==1:
            pages=response.xpath('//div[@class="page"]/a/@href')[-2].extract()
            pages=pages.split("_")[-1].split(".")[0].replace(" ","")
            pages=int(pages)
            if pages >= 5:
                pages = 5
            for next_page in range(2, pages):
                next_url=urljoin(response.url,f"index_{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})





            

                   


