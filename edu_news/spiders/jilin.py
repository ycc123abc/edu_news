import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "jilin"
    allowed_domains = ["jyt.jl.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["http://jyt.jl.gov.cn/zwgk/zcjd/",   #政策解读
                  "http://jyt.jl.gov.cn/zwgk/ggl/",         #公告栏
                   "http://jyt.jl.gov.cn/zwgk/wjtz/",           #文件通知
                   "http://jyt.jl.gov.cn/zyhd/",              #重要活动
                   "http://jyt.jl.gov.cn/jydt/xdt/index.htm",   #各地各高校动态
                   "http://jyt.jl.gov.cn/jydt/gjssdt/",  #国家省级动态


    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            self.wait_ele="//table[@class='table1 navBlock']/tbody/tr/td/table[2]/tbody/tr/td[1]/table[1]/tbody/tr"
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
                item['title']=zixun.xpath("./td[1]/a[@class='style_ys03']/text()")[0].extract()
                
                item['time']=zixun.xpath("./td[2]/text()")[0].extract()
                
                
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="吉林省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./td[1]/a[@class='style_ys03']/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                item['source_name']=response.xpath("//a[@class='CurrChnlCls']/text()")[-1].extract()
   
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
                page=response.xpath("//div[@id='pages']/a[7]/@href")[0].extract()
                page=page.split("_")[-1].split(".")[0]
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page-1}.htm")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})






            

                   


