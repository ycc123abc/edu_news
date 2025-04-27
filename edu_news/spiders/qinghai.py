import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "shandong"
    allowed_domains = ["jyt.qinghai.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jyt.qinghai.gov.cn/xw/jydt/",  #教育动态
                      "https://jyt.qinghai.gov.cn/xw/zwyw/",  #政务要闻
                    "https://jyt.qinghai.gov.cn/gk/tzgg/",  #通知公告
                    "https://jyt.qinghai.gov.cn/gk/wsgs/", #网上公示
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="青海省教育厅"
            self.wait_ele="//ul[@id='idul']/li[2]"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    

    def redis_check(self, item):
        unique_str = f"{item['title']}{item['time']}"
        fingerprint=hashlib.md5(unique_str.encode()).hexdigest()

        self.redis_key = f"news_fingerprints:{self.name}"
        print(f"当前指纹：{fingerprint}")
        # 检查指纹是否已存在
        if self.redis_conn.sismember(self.redis_key, fingerprint):
            return 1
        else:
            # 存储新指纹
            self.redis_conn.sadd(self.redis_key, fingerprint)
            return 0


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath("//ul[@id='idul']/li")
        for zixun in zixuns:
            item=EduNewsItem()
            item['title']=zixun.xpath("./a/text()")[0].extract()
            print(item['title'])
            item['time']=zixun.xpath("./span/text()")[0].extract()
            item['source_web_name']=self.source_web_name
            patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
            item['url']=patrurl
            item['source_url']=response.url
            source_name=response.xpath("//div[@id='r1']/p[1]/a/text()")
            item['source_name']=source_name[0].extract()
            current_time=time.localtime()
            item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            if not self.redis_check(item):
                yield item
 






            

                   


