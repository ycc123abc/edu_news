import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "hubei"
    allowed_domains = ["jyt.hubei.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jyt.hubei.gov.cn/bmdt/szyw/",             #时政要闻
                  "https://jyt.hubei.gov.cn/bmdt/dtyw/",               #动态要闻
                  "https://jyt.hubei.gov.cn/bmdt/tzgg/",                    #通知公告
                   "https://jyt.hubei.gov.cn/bmdt/gxhptlm/mtjj/",           #媒体聚焦
                   "https://jyt.hubei.gov.cn/bmdt/gxhptlm/cxal/",                #创新案例
                   "https://jyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/",        #规范性文件
                   "https://jyt.hubei.gov.cn/zfxxgk/zc_GK2020/zcjd_GK2020/",          #政策解读
                   
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            self.source_web_name="湖北省教育厅"
            if "GK2020" in url:
                wait_ele="//ul[@class='info-list']/li"
                page_xpath="//a[6]"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}","page_xpath":page_xpath})
            else:
                wait_ele="//li[@class='col-md-6']"
                page_xpath="//div[@class='black2']/a[6]"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}","page_xpath":page_xpath})


            

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
        wait_ele=response.meta.get("wait_ele").replace("xpath:","")
        has_new = True
        zixuns=response.xpath(wait_ele)
        n=0
        if  not zixuns:
            has_new=False
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath(".//a/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","")
                if "GK2020" in response.url:
                    item['time']=zixun.xpath("./span/text()")[0].extract()
                else :
                    tt=zixun.xpath("./div[@class='calendar']//text()")[1].extract()+"-"+zixun.xpath("./div[@class='calendar']//text()")[0].extract()
                    item['time']=tt.replace("\n","").replace("\t","").replace(" ","")
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']=self.source_web_name
                patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url

                if "szyw" in response.url:
                    item['source_name']="时政要闻"
                elif "dtyw" in response.url:
                    item['source_name']="动态要闻"
                elif "tzgg" in response.url:
                    item['source_name']="通知公告"
                elif "mtjj" in response.url:
                    item['source_name']="媒体聚焦"
                elif "cxal" in response.url:
                    item['source_name']="创新案例"
                elif "gfxwj" in response.url:
                    item['source_name']="规范性文件"
                elif "zcjd" in response.url:
                    item['source_name']="政策解读"

                
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
                page_xpath=response.meta.get("page_xpath","")
                try:
                    page=response.xpath(page_xpath)[0].extract()
                    page=page.split("_")[-1].split(".")[0]
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page-1}.shtml")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})






            

                   


