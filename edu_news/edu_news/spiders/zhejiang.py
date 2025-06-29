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
    
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://jyt.zj.gov.cn/col/col1543973/index.html",   #图文报道
                  "https://jyt.zj.gov.cn/col/col1543974/index.html",         #教育动态
                  "https://jyt.zj.gov.cn/col/col1532992/index.html",            #新闻发布会
                   "https://jyt.zj.gov.cn/col/col1532836/index.html",           #媒体关注
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://div[@class='default_pgContainer']/ul/li"})


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)

        has_new = True
        zixuns=response.xpath("//div[@class='default_pgContainer']/ul/li")
        for zixun in zixuns:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                item['time']=zixun.xpath("./span/text()")[0].extract()
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

        if current_page==1 :   
            pages=response.xpath("//span[@class='default_pgTotalRecord']/text()")[0].extract()
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                if "col1543973" in response.url or "col1543974" in response.url:
                    part_url=f"?uid=4729348&pageNum={next_page}"
                else:
                    part_url=f"?uid=4735063&pageNum={next_page}"
                next_url = urljoin(response.url,part_url )
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': next_page,"wait_ele":"xpath://div[@class='default_pgContainer']/ul/li"})



            

                   


