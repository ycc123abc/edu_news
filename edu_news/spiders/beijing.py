import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "beijing"
    allowed_domains = ["jw.beijing.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jw.beijing.gov.cn/jyzx/jyxw/",   #教育新闻
                  "https://jw.beijing.gov.cn/jyzx/spxw/",         #视频新闻
                  "https://jw.beijing.gov.cn/xxgk/zxxxgk/",            #最新信息公开
                   "https://jw.beijing.gov.cn/xxgk/2024zcjd/",           #政策解读
                   "https://jw.beijing.gov.cn/xxgk/2024zcwj/2024xzgfwj/",      #行政规范性文件
    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://div[@class='announce_list a-hov-c']/ul"})
    


            

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

        has_new = True
        zixuns=response.xpath("//div[@class='announce_list a-hov-c']/ul/li")
        n=0
        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                
                item['time']=zixun.xpath("./span/text()")[0].extract()
                
                
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="北京省教育委员会"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                item['source_name']=zixun.xpath("//a[@class='CurrChnlCls'][3]/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                self.logger.error(f"Error parsing item: {e}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                page=response.xpath("//a[7]/@href")[0].extract()
                try:
                    page=page.split("_")[-1].split(".")[0]
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":"xpath://div[@class='announce_list a-hov-c']/ul"})






            

                   


