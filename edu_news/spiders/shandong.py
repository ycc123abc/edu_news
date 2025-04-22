import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "shandong"
    allowed_domains = ["edu.shandong.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["http://edu.shandong.gov.cn/col/col11969/index.html",   # 工作动态
                  "http://edu.shandong.gov.cn/col/col11972/index.html",         #战线联播
                   "http://edu.shandong.gov.cn/col/col11973/index.html",           #新闻发布会
                   "http://edu.shandong.gov.cn/col/col11974/index.html",  #厅长办公会
                   "http://edu.shandong.gov.cn/col/col11975/index.html", #媒体聚焦
                   "http://edu.shandong.gov.cn/col/col278347/index.html", #政策解读
                   "http://edu.shandong.gov.cn/col/col124275/index.html",# 鲁教发
                   "http://edu.shandong.gov.cn/col/col124276/index.html",#鲁教字
                   "http://edu.shandong.gov.cn/col/col124277/index.html",# 鲁教函
                   "http://edu.shandong.gov.cn/col/col11990/index.html",#政策文件
                   "http://edu.shandong.gov.cn/col/col11992/index.html" ,#政策解读
                   "http://edu.shandong.gov.cn/col/col11982/index.html", #通知公告
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="山东省教育厅"
            self.global_page_num[url]=None
            self.wait_ele="//div[@class='default_pgContainer']/li"
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
        has_new = True
        zixuns=response.xpath(wait_ele)
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
                item['source_web_name']=self.source_web_name
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                source_name=response.xpath("//div[@class='dqwz_box']/table/tbody/tr/td[2]/table/tbody/tr/td/a/text()")
                if len(source_name)>2:
                    item['source_name']=source_name[2].extract()
                else:
                    item['source_name']=source_name[1].extract()
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
                page=response.xpath("//span[@class='default_pgTotalPage']/text()")[0].extract()
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"?uid=686126&pageNum={next_page}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})






            

                   


