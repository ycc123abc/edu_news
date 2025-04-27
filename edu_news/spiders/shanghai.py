import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "shanghai"
    allowed_domains = ["edu.sh.gov.cn"]
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://edu.sh.gov.cn/xwzx_bsxw/index.html",   #本市教育新闻
                  "https://edu.sh.gov.cn/xwzx_gnxw/index.html",         #国内教育新闻
                  "https://edu.sh.gov.cn/xwzx_xxgz/index.html",            #信息关注
                   "https://edu.sh.gov.cn/jyzt_index/",           #教育专题
                   "https://edu.sh.gov.cn/xwzx_tpxw/index.html",      #图片新闻
                   "https://edu.sh.gov.cn/xwzx_jyjb/index.html",            #教育简报
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://ul[@id='listContent']/li"})



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
        zixuns=response.xpath("//ul[@id='listContent']/li")
        if  not zixuns:
            has_new=False
        n=0
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                try:
                    item['time']=zixun.xpath("./span[contains(@class,'listTime')]/text()")[0].extract()
                except:
                    item['time']=""
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']="上海市教育委员会"
                patrurl=zixun.xpath("./a/@href")[0].extract()
                item['url']=urljoin(response.url,patrurl)
                item['source_url']=response.url
                try:
                    item['source_name']=response.xpath("//div[@class='top']/div/h3/a/font/text()")[0].extract()
                except:
                    item['source_name']=response.xpath("//div[@class='top']/div/h3/text()")[0].extract()
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
                try:
                    page=response.xpath("//div[@class='whj_padding whj_color']/text()")[0].extract()
                    page=page.replace("共","").replace("页","")    
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":"xpath://ul[@id='listContent']/li"})




            

                   


