from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scrapy.spiderloader import SpiderLoader
if __name__ == "__main__":
    settings = get_project_settings()
    spider_loader = SpiderLoader(settings)
    process = CrawlerProcess(settings)
    
    # 获取所有爬虫名称
    for spider_name in spider_loader.list():
        process.crawl(spider_name)
    
    process.start()