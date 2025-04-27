import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "tianjing"
    allowed_domains = ["jy.tj.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jy.tj.gov.cn/ZWGK_52172/TZGG/",   #通知公告
                  "https://jy.tj.gov.cn/ZWGK_52172/zcwj/sjwwj/index.html",         #市教委文件
                   "https://jy.tj.gov.cn/ZWGK_52172/zcjd_1/index.html",           #政策解读
                   "https://jy.tj.gov.cn/JYXW/TJJY/index.html",              #天津教育
                   "https://jy.tj.gov.cn/JYXW/GNJY/index.html",        #国内教育
                   "https://jy.tj.gov.cn/JYXW/JCJY/index.html",          #基层教育
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None

            wait_ele="//ul[@class='common-list-right-list']/li"
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
                item['title']=zixun.xpath("./a/p[@class='list-content']/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./p[@class='list-date']/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")

                item['source_name']=zixun.xpath("//a[@class='tagcolor']/text()")[-1].extract().replace(" ","").replace("\n","").replace("\t","")

                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="天津市教育委员会"
                patrurl=zixun.xpath("./a/@onclick")[0].extract()
                patrurl=patrurl.replace("isDownLoad(this,'","").replace("')","")
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
        if "TZGG" in response.url:
            has_new=False
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                try:
                    page=response.xpath("//div[@class='page-list']/span[2]/text()")[0].extract()
                    page=page.replace("共","").replace("页","")
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url=urljoin(response.url,f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})






            

                   


