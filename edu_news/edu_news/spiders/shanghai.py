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
    def start_requests(self):
        start_urls = ["https://edu.sh.gov.cn/xwzx_bsxw/index.html",   #本市教育新闻
                  "https://edu.sh.gov.cn/xwzx_gnxw/index.html",         #国内教育新闻
                  "https://edu.sh.gov.cn/xwzx_xxgz/index.html",            #信息关注
                   "https://edu.sh.gov.cn/jyzt_index/",           #教育专题
                   "https://edu.sh.gov.cn/xwzx_tpxw/index.html",      #图片新闻
                   "https://edu.sh.gov.cn/xwzx_jyjb/index.html",            #教育简报
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"_url":url,"wait_ele":"xpath://ul[@id='listContent']/li"})



    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)
        zixuns=response.xpath("//ul[@id='listContent']/li")

        for zixun in zixuns:
            try:
                item=EduNewsItem()
                item['title']=zixun.xpath("./a/text()")[0].extract()
                try:
                    item['time']=zixun.xpath("./span[contains(@class,'listTime')]/text()")[0].extract()
                except:
                    item['time']=""
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



        
        if current_page==1 :   
            pages=response.xpath("//div[@class='whj_padding whj_color']/text()")[0].extract()
            pages=pages.replace("共","").replace("页","")    
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"index_{next_page}.html")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': 0,"wait_ele":"xpath://ul[@id='listContent']/li"})




            

                   


