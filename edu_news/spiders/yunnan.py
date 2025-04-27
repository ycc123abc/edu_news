import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "yunnan"
    allowed_domains = ["jyt.yn.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jyt.yn.gov.cn/article/category/38d5f8d6af024bd0abe28cc484b18af0-1",   #教育信息
                  "https://jyt.yn.gov.cn/article/category/b99635e859f74b70b0d855812d7452fc-1",         #政策文件
                   "https://jyt.yn.gov.cn/article/category/fb23c6e425a14040a8efbef2fa58e43f-1",           #公式公告
                   "https://jyt.yn.gov.cn/article/category/4bd1bac5820642cfb7e2cf7af02f1484-1",              #政策解读
    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            if "38d5f8d6af024bd0abe28cc484b18af0" in url:
                wait_ele="//div[@class='jyxxlb']/div[2]/div[@class='jyxxnr1']"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//div[@class='yemian']/ul[1]/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})


            

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
        has_new = True
        zixuns=response.xpath(wait_ele)
        n=0
        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./span/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                if  "38d5f8d6af024bd0abe28cc484b18af0" in response.url:
                    item['source_name']="教育信息"
                else:
                    item['source_name']=response.xpath("//title/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="云南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                has_new=False
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                page=response.xpath("//span[contains(text(), '条记录')]/text()")[0].extract()
                page=page.split("/")[-1].split("页")[0].replace(" ","")
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url=response.url.split("-")[0]+f"-{next_page}"
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})






            

                   


