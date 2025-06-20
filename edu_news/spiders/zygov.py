import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import traceback
class ZygovSpider(scrapy.Spider):
    name = "zygov"
    allowed_domains = ["www.gov.cn"]
    
    global_page_num:dict={}

    def start_requests(self):
        start_urls = ["https://www.gov.cn/yaowen/liebiao/home.htm",   #要闻最新
                  "https://www.gov.cn/hudong/hygq/lyhf/",         #留言回复
                  "https://www.gov.cn/zhengce/jiedu/",            #政策解读
                   "https://www.gov.cn/zhengce/zuixin/",           #最新政策
                   "https://www.gov.cn/lianbo/bumen/home.htm",      #部门动态
                   "https://www.gov.cn/lianbo/fabu/",            #新闻发布
                   "https://www.gov.cn/lianbo/difang/"  ,             #地方动态
        ]
        for url in start_urls:
            print(url)

            yield scrapy.Request(url=url, callback=self.parse,meta={"page":1,"wait_ele":"xpath://div[@class='list list_1 list_2']/ul/li"})


    def parse(self, response):
        print(response.url,"开始爬虫")
        current_page = response.meta.get('page', 1)

        zixuns=response.xpath("//div[@class='list list_1 list_2']/ul/li")
        for zixun in zixuns:
            try:
                item=EduNewsItem()
                try:
                    item['title']=zixun.xpath("./h4/a//text()")[0].extract()
                except:
                    print("标题获取失败",response.url)
                    continue
                item['time']=zixun.xpath("./h4/span/text()")[0].extract()
                patrurl=zixun.xpath("./h4/a/@href")[0].extract()
                item['url']=urljoin(response.url,patrurl)
                item['source_web_name']="中央政府网"
                item['source_url']=response.url
                item['source_name']=response.xpath("//span[@class='noline']/a/text()")[0].extract()
                current_time=time.localtime()
                item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                yield item
            except :
                self.logger.error(f"Error parsing item: {traceback.format_exc()}")
            
                

        if current_page==1 :   
            pages=response.xpath("//span[@class='red']/text()")[0].extract()
            pages=int(pages)
            if pages >= 5:
                pages = 5
            if pages<=1 :
                return
            for next_page in range(2, pages + 1):
                next_url = urljoin(response.url, f"home_{next_page-1}.htm")
                yield scrapy.Request(url=next_url, callback=self.parse,meta={"page":2,"wait_ele":"xpath://div[@class='list list_1 list_2']/ul/li"})



            

                   


