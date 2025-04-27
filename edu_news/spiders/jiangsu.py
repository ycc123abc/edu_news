import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "jiangsu"
    allowed_domains = ["jyt.jiangsu.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jyt.jiangsu.gov.cn/col/col82269/index.html?uid=396302&pageNum=1",   #时政要闻
                  "https://jyt.jiangsu.gov.cn/col/col57807/index.html",         #教育要闻
                  "https://jyt.jiangsu.gov.cn/col/col58320/index.html",            #通知公告
                   "https://jyt.jiangsu.gov.cn/col/col57812/index.html",           #市县动态
                   "https://jyt.jiangsu.gov.cn/col/col57813/index.html",      #高校动态
                   "https://jyt.jiangsu.gov.cn/col/col57810/index.html",            #媒体聚焦
                   "https://jyt.jiangsu.gov.cn/col/col57816/index.html"  ,             #图片新闻

    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://div[@class='default_pgContainer']/li[@class='cf']"})
    


            

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
        zixuns=response.xpath("//div[@class='default_pgContainer']/li[@class='cf']")
        n=0
        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                
                item['time']=zixun.xpath("./span[@class='fr']/text()")[0].extract()
                
                
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="江苏省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                item['source_name']=zixun.xpath("//div[@class='currentPosition']/table/tbody/tr/td[3]/table/tbody/tr/td[2]/a/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
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
                next_url = urljoin(response.url, f"?uid=396302&pageNum={next_page}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":"xpath://div[@class='default_pgContainer']/li[@class='cf']"})






            

                   


