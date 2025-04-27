import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import json
from lxml import etree
class ZygovSpider(scrapy.Spider):
    name = "gansu"
    allowed_domains = ["jyt.gansu.gov.cn"]
    global_page_num:dict={}
    redis_conn =Redis(host="127.0.0.1", port=6379, db=7)
    def start_requests(self):
        start_urls = ["https://jyt.gansu.gov.cn/common/search/6ed9cac952e94022bd5bd213764b983d?sort=&_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_rangeTimeLt=&_channelName=&page=1",   #媒体聚焦
                   "https://jyt.gansu.gov.cn/common/search/c7df0c0ea0b7444d9744d4a6c1fcca4b?sort=&_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_rangeTimeLt=&_channelName=&page=1",           #教育动态
                   "https://jyt.gansu.gov.cn/common/search/695dc7247ea148ad8e01ad5988132d63?sort=&_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_rangeTimeLt=&_channelName=&page=1",          #教育要闻

                 
        ]
        cookies="Path=/;4hP44ZykCTt5=60S_y1XScZEqaKbtEO1FtH8s7Xf3sOhXHTEcwTR3CAKqoUnIWLJ3DVz8bh2QlRxD3QrISoTBCsIcuOqM53NDkuva;7d0f4f97e8317b129e=9aa103edd849aa2ee90db4924883ab51;4hP44ZykCTt5P=0EhKP1Kr7KjL6nHuzjl3hdnjX79StnfJ.dd_2GC._rVFH_q6SeBNp2_bPXRMdlI3RDKbae72Fpvbv5y5bnf8oAqlrKtHoXBW7BH70kF4Szdq_OKMTM_W7Id7u9G39bqYZaHJ51xCCLUWUkeKtFvssu0GslEm0HoPV7.K4zdxPn33SE_R85Z2V0gEhEBgIFu2K7_HIsPikjRYnylfVXqWZgt7dIsx2ebKkJmiSI1r9ghQtrpiGLiB3YZDJge4aDWrN"
        for url in start_urls:
            if "6ed9cac952e94022bd5bd213764b983d" in url:
                # for i in range(1, 232):
                for i in range(1, 10):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,cookies=cookies)

            elif "c7df0c0ea0b7444d9744d4a6c1fcca4b" in url:
                # for i in range(1, 530):
                for i in range(1, 10):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,cookies=cookies)

            elif "695dc7247ea148ad8e01ad5988132d63" in url:
                # for i in range(1, 211):
                for i in range(1, 10):
                    url_=url.replace("page=1","page="+str(i))
                    yield scrapy.Request(url=url_, callback=self.parse,cookies=cookies)
            

            


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
        tree=etree.HTML(response.text)
        json_text=tree.xpath('//pre')[0].text
        print(json_text)
        response_json  =  json.loads(json_text)
        results = response_json["data"]["results"]
        for result in results:
            item=EduNewsItem()
            item["title"]=result["title"]
            item["url"]=urljoin(response.url,result["url"])
            item["time"]=result["publishedTimeStr"]
            current_time=time.localtime()
            item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            item['source_url']=response.url
            item['source_web_name']="甘肃省教育厅"
            item['source_name']=result["channelName"]

            if not self.redis_check(item):
                yield item
            







            

                   


