from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 如果你的爬虫在 spiders 目录下
from edu_news.spiders import neimenggu, anhui,liaoning,yunnan,xizang,ningxia,sichuan,chongqing,guizhou,hainan,tianjing,xinjiang,heilongjiang,gansu,fujian
from edu_news.spiders import qinghai

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    
    # 添加多个爬虫
    # process.crawl(neimenggu.ZygovSpider)
    # process.crawl(liaoning.ZygovSpider)
    # process.crawl(yunnan.ZygovSpider)
    # process.crawl(xizang.ZygovSpider)
    # process.crawl(ningxia.ZygovSpider)
    # process.crawl(sichuan.ZygovSpider)
    # process.crawl(chongqing.ZygovSpider)
    process.crawl(qinghai.ZygovSpider)
    # process.crawl(guizhou.ZygovSpider)
    # process.crawl(hainan.ZygovSpider)
    # process.crawl(tianjing.ZygovSpider)
    # process.crawl(xinjiang.ZygovSpider)
    # process.crawl(heilongjiang.ZygovSpider)
    # process.crawl(gansu.ZygovSpider)
    # process.crawl(fujian.ZygovSpider)
    process.start()  # 所有爬虫会在同一进程中运行