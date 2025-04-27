import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib

class ZygovSpider(scrapy.Spider):
    name = "neimenggu"
    allowed_domains = ["jyt.nmg.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)

    def start_requests(self):
        start_urls = ["https://jyt.nmg.gov.cn/jydt/zhxx/",   #  综合信息
                  "https://jyt.nmg.gov.cn/zwgk/tzgg_25132/",         # 通知公告
                  "https://jyt.nmg.gov.cn/zfxxgk/fdzdgknr/zcjd_17374/index.html",    #政策解读
                  "https://jyt.nmg.gov.cn/zfxxgk/fdzdgknr/bmwj/index.html",          #部门文件
        ]

        for url in start_urls:
            print(url)
            self.source_web_name="内蒙古省教育厅"
            self.global_page_num[url]=None
            if "fdzdgknr" not in url:
                self.wait_ele="//div[@class='tygl_con_con wzlm_con_con']/ul/li"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}","change":True})
            else:
                self.wait_ele="//tbody/tr"
                yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}","change":True})

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
                if "fdzdgknr" not in response.url:
                    item['title']=zixun.xpath("./a/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                    item['time']=zixun.xpath("./span/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                    item['source_name']=response.xpath("//div[@class='tygl_con_tit']/span/text()")[0].extract()
                    patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                    item['url']=patrurl
                else:
                    item['title']=zixun.xpath("./td[2]/a/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                    item['time']=zixun.xpath("./td/text()")[-1].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                    item['source_name']=response.xpath("//h3/text()")[0].extract().replace("\n","").replace("\t","").replace(" ","").strip()
                    patrurl=urljoin(response.url,zixun.xpath(".//a/@href")[0].extract())
                    item['url']=patrurl
                if self.redis_check(item):
                    n+=1
                    if n>=len(zixuns):
                        has_new=False
                    continue
                item['source_web_name']=self.source_web_name
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except:
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')
        if has_new:
            
            if self.global_page_num[_url] is None:
                # 获取总页数
                
                try:
                    page=response.xpath("//div[@class='xll_pagebox']/span[1]/font/text()")[0].extract()
                    page=page.split("共")[-1].split("页")[0]
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    if "fdzdgknr/zcjd_17374" in response.url:
                        self.global_page_num[_url]=8
                    elif "fdzdgknr/bmwj" in response.url:
                        self.global_page_num[_url]=115
                    else:
                        self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url, f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}","change":True})






            

                   


