import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "zygov"
    allowed_domains = ["www.gov.cn"]
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://www.gov.cn/yaowen/liebiao/home.htm",   #要闻最新
                  "https://www.gov.cn/hudong/hygq/lyhf/",         #留言回复
                  "https://www.gov.cn/zhengce/jiedu/",            #政策解读
                   "https://www.gov.cn/zhengce/zuixin/",           #最新政策
                   "https://www.gov.cn/lianbo/bumen/home.htm",      #部门动态
                   "https://www.gov.cn/lianbo/fabu/",            #新闻发布
                   "https://www.gov.cn/lianbo/difang/"  ,             #地方动态

        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url})



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
        zixuns=response.xpath("//div[@class='list list_1 list_2']/ul/li")
        if  not zixuns:
            has_new=False
        n=0
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./h4/a/text()")[0].extract()
                item['time']=zixun.xpath("./h4/span/text()")[0].extract()
                patrurl=zixun.xpath("./h4/a/@href")[0].extract()
                item['url']=urljoin(response.url,patrurl)
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="中央政府网"
                item['source_url']=response.url
                item['source_name']=response.xpath("//span[@class='noline']/a/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                print(item)
                yield item
            except :
                self.logger.error(f"Error parsing item: {traceback.format_exc()}")
            
                
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            if self.global_page_num[_url] is None:
                page=response.xpath("//span[@class='red']/text()")[0].extract()
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"home_{next_page-1}.htm")
                yield scrapy.Request(url=next_url, callback=self.parse,meta={"page":1,"_url":_url})
            



            

                   


