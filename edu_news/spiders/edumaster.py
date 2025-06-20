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

    def start_requests(self):
        for url in self.start_urls:
            wait_ele="//ul[@id='list']/li"
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":f"xpath:{wait_ele}"})


    def parse(self, response):
        # 解析当前页面的数据
        current_page = response.meta.get('page', 1)
        wait_ele=response.meta.get('wait_ele').replace("xpath:","")
        titles=response.xpath(wait_ele)
        for title in titles:
                item=EduNewsItem()
                item['title']=title.xpath("./a/text()").extract_first()
                item['time']=title.xpath("./span/text()").extract_first()

                url=urljoin(response.url,title.xpath("./a/@href").extract_first())
                item["url"]=url
                item['source_web_name']="教育部"
                item['source_name']=response.xpath("//h2/text()").extract_first()
                item['source_url']=response.url
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item

        if current_page==1:
                pages=response.xpath("//li[@class='mhide'][3]/text()")[0].extract().split("/")[1]
                pages = int(pages)
                if pages >= 5:
                    pages = 5
                for next_page in range(2, pages):
                    next_url = urljoin(response.url,f"index_{next_page-1}.html")
                    yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":f"xpath:{wait_ele}"})
                


