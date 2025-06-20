import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "chongqing"
    allowed_domains = ["jw.cq.gov.cn"]

    def start_requests(self):
        start_urls = [
                   "https://jw.cq.gov.cn/zwxx_209/jdtp/index.html",        #焦点图片
                   "https://jw.cq.gov.cn/zwxx_209/gggs/index.html",          #公告公示
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/zhxx/index.html",      #综合信息
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/qxxx/index.html",          #区县信息
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/gxxx/index.html",          #高校信息
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/zsdwxx/index.html",         #直属单位信息
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/mtxx/spxw/index.html",#视频新闻
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/mtxx/mtxw/index.html", #媒体新闻
                   "https://jw.cq.gov.cn/zwxx_209/bmdt/ddxx/index.html"  #督导信息

    
        ]
        for url in start_urls:
            print(url)
            wait_ele="//div[@class='information-l-content']/ul/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"change":True})



    def parse(self, response):
        current_page = response.meta.get('page', 1)
        zixuns=response.xpath("//div[@class='information-l-content'][2]/ul/li")
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()").extract_first().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./span/text()").extract_first().replace(" ","").replace("\n","").replace("\t","")
                item['source_name']=zixun.xpath("//a[@class='title-universal']/text()").extract_first().replace(" ","").replace("\n","").replace("\t","")
                item['source_web_name']="重庆市教育委员会"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href").extract_first().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)

                yield item

        if current_page==1:
                pages=response.selector.re("createPage\((\d+)")[0]
                pages = int(pages)
                if pages >= 5:
                    pages = 5
                for next_page in range(2, pages):
                    next_url = urljoin(response.url, f"index_{next_page-1}.html")
                    yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0})






            

                   


