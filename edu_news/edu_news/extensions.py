# 在Scrapy项目关闭时关闭PagePool的钩子（例如在扩展中实现）
from scrapy import signals as scrapy_signals
from edu_news.middlewares import PagePool
class PagePoolCleanup:
    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.engine_stopped, signal=scrapy_signals.engine_stopped)
        return ext

    def engine_stopped(self):
        if PagePool._instance:
            PagePool._instance.close()


