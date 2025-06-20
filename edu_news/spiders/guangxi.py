import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "guangxi"
    allowed_domains = ["jyt.gxzf.gov.cn"]
    global_page_num:dict={}
    

    def start_requests(self):
        start_urls = ["http://jyt.gxzf.gov.cn/jyxw/jyyw/",   #教育工作动态
                  "http://jyt.gxzf.gov.cn/zfxxgk/fdzdgknr/tzgg_58179/",         #通知公告
                   "http://jyt.gxzf.gov.cn/ztzl/zzgk/",           #粽仔说高考


    
        ]
        for url in start_urls:
            print(url)
            self.global_page_num[url]=None
            self.wait_ele="//ul[@class='more-list']/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{self.wait_ele}"})
    


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        zixuns=response.xpath(wait_ele)
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                item['time']=zixun.xpath("./span/text()")[0].extract()
                item['source_web_name']="广西省教育厅"
                patrurl=urljoin(response.url,zixun.xpath("./a/@href")[0].extract())
                item['url']=patrurl
                item['source_url']=response.url
                if "/jyxw/jyyw/" in response.url:
                    item['source_name']="教育工作动态"
                elif "tzgg_58179" in response.url:
                    item['source_name']="通知公告"
                elif "zzgk" in response.url:
                    item['source_name']="粽仔说高考"    
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except Exception as e:
                self.logger.error(f"Error processing item: {traceback.format_exc()}")
            
        next_page = current_page + 1
        # 动态生成下一页请求
        _url=response.meta.get('_url')

        if current_page==1:
            pages=response.xpath("//div[@class='more-page']/a[last()-4]/@href")[0].extract()
            pages=int(pages.split("_")[-1].split(".")[0])
            if pages >= 5:
                pages = 5
            for next_page in range(2, pages):
                next_url = urljoin(response.url, f"index_{next_page-1}.shtml")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"_url":_url,"wait_ele":f"xpath:{wait_ele}"})





            

                   


