import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "hunan"
    allowed_domains = ["jyt.hunan.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
    wait_ele=None
    def start_requests(self):
        start_urls = ["https://jyt.hunan.gov.cn/jyt/sjyt/jyyw/2019_zfxxgk_listsub.html",             #教育要闻
                  "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/jykx/jykx_1/index.html",               #教育快讯
                  "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/bwdt1/",                    #部委动态
                   "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/szdt/index.html",           #一线采风 市州动态
                   "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/gxdt/index.html",                #一线采风 高校动态
                #    "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/c100959/index.html",         #文件库
                "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/tzgg/index.html",                 #通知公告
                "https://jyt.hunan.gov.cn/jyt/sjyt/xxgk/zcfg/zcjd/index.html"             #政策解读

    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            self.wait_ele="//ul[@class='list_gkzd_content']/li"
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

        has_new = True
        zixuns=response.xpath("//ul[@class='list_gkzd_content']/li")
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
                item['source_web_name']="湖南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                if "jyyw" in response.url:
                    item['source_name']="教育要闻"
                elif "xxgk" in response.url:
                    item['source_name']="教育快讯"
                elif "bwdt" in response.url:
                    item['source_name']="部委动态"
                elif "szdt" in response.url:
                    item['source_name']="一线采风 市州动态"
                elif "gxdt" in response.url:
                    item['source_name']="一线采风 高校动态"
                elif "tzgg" in response.url:
                    item['source_name']="通知公告"
                elif "zcfg" in response.url:
                    item['source_name']="政策解读"

                
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
                try:
                    page=response.xpath("//li[@class='end_page']/a/@href")[0].extract()
                    page=page.split("_")[-1].split(".")[0]
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{self.wait_ele}"})






            

                   


