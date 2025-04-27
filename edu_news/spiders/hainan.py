import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "hainan"
    allowed_domains = ["edu.hainan.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = [
                   "http://edu.hainan.gov.cn/edu/zxjd/tylist.shtml",          #最新解读
                   "http://edu.hainan.gov.cn/common/search/459d0a8a28674196bc67bbfa4db378a8?sort=publishedTime&_isAgg=false&_isJson=false&_pageSize=12&_template=edu&_rangeTimeGte=&_channelName=&page=1",          #公示公告   
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            if "common" in url:
                wait_ele="//div[@class='cen-div-1 mar-t']/div"
                yield scrapy.Request(url=url, callback=self.first_parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})
            else:
                wait_ele="//dl/li"
                yield scrapy.Request(url=url, callback=self.second_parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})

       

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


    def first_parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        has_new = True
        zixuns=response.xpath(wait_ele)[:-1]
        n=0
        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./div[@class='list-right_title fon_1']/a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./table/tbody/tr/td[1]/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","").replace("发布时间：","")
                item['source_name']=(zixun.xpath("//div[@class='list_left_title']/text()"))[0].extract().replace(" ","").replace("\n","").replace("\t","")

                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue

                item['source_web_name']="海南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./div[@class='list-right_title fon_1']/a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                has_new=False
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                page=response.xpath("//a[contains(text(), '末页')]/@href")[0].extract()
                page=page.split("=")[-1]
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url=response.url[:-1]+str(next_page)
                yield scrapy.Request(next_url, callback=self.first_parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})

            
    def second_parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        has_new = True
        zixuns=response.xpath(wait_ele)
        print(wait_ele,zixuns,"zixuns")
        n=0
        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","")
                item["time"]=zixun.xpath("./em/text()")[0].extract().replace(" ","").replace("\n","").replace("\t","").replace("发布时间：","")
                item['source_name']=(zixun.xpath("//ul[@class='htm_zb-01']/h2/text()"))[0].extract().replace(" ","").replace("\n","").replace("\t","")

                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue

                item['source_web_name']="海南省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract().replace(" ","").replace("\n","").replace("\t",""))
                item['url']=patrurl
                item['source_url']=response.url
                
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                has_new=False
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                page=response.xpath("//a[contains(text(), '末页')]/@href")[0].extract()
                page=page.split("_")[-1].split(".")[0]
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url=urljoin(response.url,f"tylist_{next_page}.shtml")
                yield scrapy.Request(next_url, callback=self.second_parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})
                   


