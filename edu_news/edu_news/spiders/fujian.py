import scrapy
from  edu_news.items  import EduNewsItem
from urllib.parse import urljoin
import time
from redis import Redis
import hashlib
import json
from lxml import etree
class ZygovSpider(scrapy.Spider):
    name = "fujian"
    allowed_domains = ["jyt.fujian.gov.cn"]
    global_page_num:dict={}
    
    def start_requests(self):
        start_urls = ["https://jyt.fujian.gov.cn/fjdzapp/search?channelid=229105&sortfield=-docorderpri%2C-docreltime&classsql=(chnlid%3D30242)*(publishyear%3D2025)&classcol=publishyear&classnum=100&classsort=0&cache=true&page=1&prepage=75",   #教育厅
                   "https://jyt.fujian.gov.cn/fjdzapp/search?channelid=229105&sortfield=-docorderpri%2C-docreltime&classsql=(chnlid%3D30245)*(publishyear%3D2025)&classcol=publishyear&classnum=100&classsort=0&cache=true&page=1&prepage=75",           #教育动态
                   "https://jyt.fujian.gov.cn/fjdzapp/search?channelid=229105&sortfield=-docorderpri%2C-docreltime&classsql=(chnlid%3D30169)*(publishyear%3D2025)&classcol=publishyear&classnum=100&classsort=0&cache=true&page=1&prepage=75",          #公告公示
                   "https://jyt.fujian.gov.cn/fjdzapp/search?channelid=229105&sortfield=-docorderpri%2C-docreltime&classsql=(chnlid%3D30170)*(publishyear%3D2025)&classcol=publishyear&classnum=100&classsort=0&cache=true&page=1&prepage=75",  #重要文件
                   "https://jyt.fujian.gov.cn/fjdzapp/search?channelid=229105&sortfield=-docorderpri%2C-docreltime&classsql=(chnlid%3D30173)*(publishyear%3D2025)&classcol=publishyear&classnum=100&classsort=0&cache=true&page=1&prepage=75",#部门政策文件解读
        ]
        # cookies="Path=/;4hP44ZykCTt5=60S_y1XScZEqaKbtEO1FtH8s7Xf3sOhXHTEcwTR3CAKqoUnIWLJ3DVz8bh2QlRxD3QrISoTBCsIcuOqM53NDkuva;7d0f4f97e8317b129e=9aa103edd849aa2ee90db4924883ab51;4hP44ZykCTt5P=0EhKP1Kr7KjL6nHuzjl3hdnjX79StnfJ.dd_2GC._rVFH_q6SeBNp2_bPXRMdlI3RDKbae72Fpvbv5y5bnf8oAqlrKtHoXBW7BH70kF4Szdq_OKMTM_W7Id7u9G39bqYZaHJ51xCCLUWUkeKtFvssu0GslEm0HoPV7.K4zdxPn33SE_R85Z2V0gEhEBgIFu2K7_HIsPikjRYnylfVXqWZgt7dIsx2ebKkJmiSI1r9ghQtrpiGLiB3YZDJge4aDWrN"
        for url in start_urls:
            # if "6ed9cac952e94022bd5bd213764b983d" in url:
            #     for i in range(1, 232):
            #         url_=url.replace("page=1","page="+str(i))
            #         yield scrapy.Request(url=url_, callback=self.parse)

            # elif "c7df0c0ea0b7444d9744d4a6c1fcca4b" in url:
            #     for i in range(1, 530):
            #         url_=url.replace("page=1","page="+str(i))
            #         yield scrapy.Request(url=url_, callback=self.parse)

            # elif "695dc7247ea148ad8e01ad5988132d63" in url:
            #     for i in range(1, 211):
            #         url_=url.replace("page=1","page="+str(i))
            #         yield scrapy.Request(url=url_, callback=self.parse)
            yield scrapy.Request(url=url, callback=self.parse)
            

            





    def parse(self, response):
        tree=etree.HTML(response.text)
        json_text=tree.xpath('//pre')[0].text
        response_json  =  json.loads(json_text)
        results = response_json["data"]
        for result in results:
            item=EduNewsItem()
            item["title"]=result["doctitle"]
            item["url"]=result["chnldocurl"]
            item["time"]=result["docreltime"]
            current_time=time.localtime()
            item['create_time']=time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            item['source_url']=response.url
            item['source_web_name']="福建省教育厅"
            item['source_name']=result["chnlname"]

            yield item
            







            

                   


