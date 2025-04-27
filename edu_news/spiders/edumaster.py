import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class EdumasterSpider(scrapy.Spider):
    name = "edumaster"
    allowed_domains = ["www.moe.gov.cn"]
    start_urls = ["http://www.moe.gov.cn/jyb_sy/shizheng/",    #时政要闻
                  "http://www.moe.gov.cn/jyb_sy/sy_jyyw/",     #教育要闻
                  "http://www.moe.gov.cn/jyb_xwfb/xw_fbh/moe_2069/xwfbh/",  #发布会   
                  "http://www.moe.gov.cn/jyb_xwfb/s271/",           #政策解读
                  "http://www.moe.gov.cn/jyb_xxgk/s5743/s5744/",    #公告公示
                  "http://www.moe.gov.cn/jyb_xwfb/s6192/s222/",     #战线链表
                  "http://www.moe.gov.cn/jyb_sjzl/s3165/",           #教育部简报
                #   "http://www.moe.gov.cn/was5/web/search?channelid=239993",    #教育部文件
                  "http://www.moe.gov.cn/jyb_xxgk/moe_1777/moe_1779/",        #其他部门文件
                  "http://www.moe.gov.cn/jyb_xxgk/moe_1777/moe_1778/" ,        #中央文件
                  "http://www.moe.gov.cn/jyb_xwfb/xw_zt/moe_357/2025/"         #专题专栏
                  ]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
    def start_requests(self):
        for url in self.start_urls:
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
        # 解析当前页面的数据
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        has_new = True
        titles=response.xpath("//ul[@id='list']/li")
        if  not titles:
            has_new=False
        n=0
        for title in titles:
            try:
                item=EduNewsItem()
                item['title']=title.xpath("./a/text()")[0].extract()
                item['time']=title.xpath("./span/text()")[0].extract()
                if self.redis_check(item):
                        n+=1
                        if n>=len(titles):
                            has_new=False
                        continue
                url=urljoin(response.url,title.xpath("./a/@href")[0].extract())
                item["url"]=url
                item['source_web_name']="教育部"
                item['source_name']=response.xpath("//h2/text()")[0].extract()
                item['source_url']=response.url
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
                page=response.xpath("//li[@class='mhide'][3]/text()")[0].extract().split("/")[1]
                try:
                    page=int(page)
                    self.global_page_num[_url]=page
                except:
                    self.global_page_num[_url]=1
            if next_page <= self.global_page_num[_url]:
                next_url = urljoin(response.url,f"index_{next_page-1}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url})

                


