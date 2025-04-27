import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "ningxia"
    allowed_domains = ["jyt.nx.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jyt.nx.gov.cn/xwdt/tzgg/index.html",   #通知公告
                  "https://jyt.nx.gov.cn/xwdt/zdhy/index.html",         #重要会议
                   "https://jyt.nx.gov.cn/xwdt/gzdt/index.html",           #工作动态
                   "https://jyt.nx.gov.cn/zwgk/zcwj/zzqzfwj/index.html",              #自治区文件
    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            if "zcwj" not in url:
                wait_ele="//ul[@class='wzlb']/a"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//div[@class='zfxxgk_zd1']"
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
                
                if "zcwj" not in response.url:
                    item['title']=zixun.xpath("./li/p/text()")[0].extract()
                    item["time"]=zixun.xpath("./li/span/text()")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    item['source_name']=zixun.xpath("//p[@class='qdwz']/text()[2]")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    patrurl=urljoin(response.url,zixun.xpath("./@href")[0].extract())
                    item['url']=patrurl
                else:
                    item['title']=zixun.xpath("./a/text()")[0].extract()
                    item["time"]=zixun.xpath("./b/text()")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    item['source_name']=zixun.xpath("//div[@class='zfxxgk_zdgktit']/a/text()")[0].extract().replace("\n","").replace(" ","").replace("\t","")
                    patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                    item['url']=patrurl
                item['source_web_name']="宁夏省教育厅"

                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
            except Exception as e:
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                try:
                    page=response.xpath("//a[@class='be']/@href")[0].extract()
                    page=page.split("_")[-1].split(".")[0].replace(" ","")
                except:
                    page=response.xpath("//a[7]/text()")[0].extract()
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url=urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})






            

                   


