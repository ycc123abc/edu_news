import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "guangdong"
    allowed_domains = ["edu.gd.gov.cn"]
    
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://edu.gd.gov.cn/jyzxnew/gdjyxw/index.html",   #广东教育新闻
                  "https://edu.gd.gov.cn/jyzxnew/tpxw/index.html",         #图片新闻
                  "https://edu.gd.gov.cn/jyzxnew/zxlb/index.html",            #战线联播
                   "https://edu.gd.gov.cn/zwgknew/jyzcfg/zc/index.html",           #章程
                   "https://edu.gd.gov.cn/zwgknew/jyzcfg/dfjyzcfg/index.html",      #地方性法规
                   "https://edu.gd.gov.cn/zwgknew/jyzcfg/gfxwj/index.html",            #规范性文件
                   "https://edu.gd.gov.cn/zwgknew/zcjd/index.html"  ,             #政策解读
                   "https://edu.gd.gov.cn/zwgknew/zbcg/index.html",        #招标采购
                   "https://edu.gd.gov.cn/zwgknew/sjfb/index.html",        #数据发布
                   "https://edu.gd.gov.cn/zwgknew/jyfzgh/index.html",        #教育发展规划
                   "https://edu.gd.gov.cn/zwgknew/gxxxgkzl/xxgkgz/index.html",        #高校信息公开
    
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://ul[@class='list']/li"})




    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)


        zixuns=response.xpath("//ul[@class='list']/li")
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()

                item['time']=zixun.xpath("./span[@class='time']/text()")[0].extract()
                item['source_web_name']="广东省教育厅"
                patrurl=zixun.xpath("./a/@href")[0].extract()
                item['url']=patrurl
                item['source_url']=response.url
                item['source_name']=zixun.xpath("//div[@class='pos']/a[3]/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
                
        if current_page==1:
                page=response.xpath("//a[@class='last']/@href")[0].extract()
                if "_" in page:
                    pages = int(page.split("_")[1].split(".")[0])
                    if pages >= 5:
                        pages = 5
                    for next_page in range(2, pages):
                        next_url = urljoin(response.url, f"index_{next_page}.html")
                        yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":"xpath://ul[@class='list']/li"})




            

                   


