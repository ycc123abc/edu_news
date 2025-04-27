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
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
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
            print(url)
            self.global_page_num[url]=None
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://ul[@class='list']/li"})



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
        zixuns=response.xpath("//ul[@class='list']/li")
        if  not zixuns:
            has_new=False
        n=0
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()

                item['time']=zixun.xpath("./span[@class='time']/text()")[0].extract()
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
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
            
                
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        print(has_new,next_page,self.global_page_num[_url])
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                page=response.xpath("//a[@class='last']/@href")[0].extract()
                try:
                    if "index." in page:
                        self.global_page_num[_url]=0
                    else:
                        page=page.split("_")[1].split(".")[0]
                        page=int(page)
                        self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1

            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":"xpath://ul[@class='list']/li"})




            

                   


