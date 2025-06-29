import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "liaoning"
    allowed_domains = ["jyt.ln.gov.cn"]
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://jyt.ln.gov.cn/jyt/jyzx/swszfxx/9fad0ecd-1.shtml",   #省委省政府信息
                  "https://jyt.ln.gov.cn/jyt/jyzx/jyyw/03ebc6c8-1.shtml",         #教育要闻
                   "https://jyt.ln.gov.cn/jyt/jyzx/zxlb/1843edeb-1.shtml",           #战线联播
                   "https://jyt.ln.gov.cn/jyt/gk/zxtz/f797aa36-1.shtml",              #最新通知
                   "https://jyt.ln.gov.cn/jyt/gk/gsgg/269bf6a1-1.shtml",   #公示公告
                   "https://jyt.ln.gov.cn/jyt/gk/jywj/2edce1e3-1.shtml",  #教育厅文件
                   "https://jyt.ln.gov.cn/jyt/gk/jywj/qtbmwj/14e3b4f1-2.shtml",  #联合发文
                   "https://jyt.ln.gov.cn/jyt/gk/zcjd/1d6b4b62-2.shtml", #政策解读
                   "https://jyt.ln.gov.cn/jyt/gk/zfxxgk/zc/xzgfxwj/ccf7ccb6-1.shtml"     #规范性文件
        ]
        for url in start_urls:
            if "xzgfxwj" in url:
                wait_ele="//li[@class='kr-body-table-block']"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//div[@class='l-gl-main cl']/ul/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})


            
    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath(".//a/text()")[0].extract()
                if  "xzgfxwj" in response.url:
                    item["time"]=zixun.xpath("./span[@class='kr-body-text kr-table-ratio4 kr-body-table-download']/text()")[0].extract().replace("\n","")
                    item['source_name']="行政规范性文件"
                else:
                    item['time']=zixun.xpath("./span/text()")[0].extract()
                    item['source_name']=response.xpath("//div[@class='sidebar_b_tittle fl']/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","")

                item['source_web_name']="辽宁省教育厅"
                patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item



        if current_page==1 :   
            pages=response.xpath('//a[@title="尾页"]/@tagname')[0].extract()
            pages=pages.split("-")[-1].split(".")[0].replace(" ","")
            print(pages)
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url=response.url.split("-")[0]+f"-{next_page}.shtml"
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})






            

                   


