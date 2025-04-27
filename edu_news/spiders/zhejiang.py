import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "zhejiang"
    allowed_domains = ["jyt.zj.gov.cn"]
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://jyt.zj.gov.cn/col/col1543973/index.html",   #图文报道
                  "https://jyt.zj.gov.cn/col/col1543974/index.html",         #教育动态
                  "https://jyt.zj.gov.cn/col/col1532992/index.html",            #新闻发布会
                   "https://jyt.zj.gov.cn/col/col1532836/index.html",           #媒体关注
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://div[@class='default_pgContainer']/ul/li"})



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
        zixuns=response.xpath("//div[@class='default_pgContainer']/ul/li")
        if  not zixuns:
            has_new=False
        n=0
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                try:
                    item['time']=zixun.xpath("./span/text()")[0].extract()
                except:
                    item['time']=""
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="浙江省教育厅"
                patrurl=zixun.xpath("./a/@href")[0].extract()
                item['url']=urljoin(response.url,patrurl)
                item['source_url']=response.url
                if "col1543973" in response.url:
                    item['source_name']="图文报道"
                elif "col1543974" in response.url:
                    item['source_name']="教育动态"
                elif "col1532992" in response.url:
                    item['source_name']="新闻发布会"
                elif "col1532836" in response.url:
                    item['source_name']="媒体关注"

                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except :
                self.logger.error(f"Error processing item: {traceback.format_exc()}")

        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            if self.global_page_num[_url] is None:
                # 获取总页数
                try:
                    page=response.xpath("//span[@class='default_pgTotalRecord']/text()")[0].extract()
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                if "col1543973" in response.url or "col1543974" in response.url:
                    part_url=f"?uid=4729348&pageNum={next_page}"
                else:
                    part_url=f"?uid=4735063&pageNum={next_page}"
                next_url = urljoin(response.url,part_url )
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":"xpath://div[@class='default_pgContainer']/ul/li"})




            

                   


