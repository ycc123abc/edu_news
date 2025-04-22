# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class EduNewsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class EduNewsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)





from DrissionPage import Chromium, ChromiumOptions
from scrapy.http import HtmlResponse
from queue import Queue
from threading import Lock, Semaphore
from scrapy import signals
from twisted.internet import threads

class PagePool:
    _instance = None
    _lock = Lock()

    def __new__(cls, pool_size=4):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__initialized = False
        return cls._instance
    def __init__(self, pool_size=4):
        if self.__initialized:
            return
        self.__initialized = True
        self.pool_size = pool_size
        self.chromium_options = ChromiumOptions()
        self.chromium_options.no_imgs(True).no_js(True)
        # self.chromium_options.headless()
        self.browser = Chromium(self.chromium_options)
        self.pages = Queue()
        self.max_pool_size=2*self.pool_size
        self.total_pages = 0
        
        # 初始化多个标签页
        for _ in range(pool_size):
            tab = self.browser.new_tab()
            self.pages.put(tab)
            self.total_pages += 1
    def get_page(self):
        if self.pages.empty() and self.total_pages < self.max_pool_size:
            with self.pool_lock:
                if self.pages.empty() and self.total_pages < self.max_pool_size:
                    tab = self.browser.new_tab()
                    self.total_pages += 1
                    return tab
        return self.pages.get()

        
    def release_page(self, page):
        page.get("about:blank")
        self.pages.put(page)

    def close(self):
        self.browser.quit()

class DrissionpageMiddleware:
    def __init__(self, pool_size=8):
        self.pool = PagePool(pool_size)
        self.browser = self.pool.browser  # 从 PagePool 中获取浏览器实例

    @classmethod
    def from_crawler(cls, crawler):
        pool_size = crawler.settings.getint('CONCURRENT_REQUESTS', 8)
        middleware = cls(pool_size)
        # 注册信号处理
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware



    
    def spider_closed(self, spider):
        """爬虫关闭时自动调用此方法"""
        # 关闭浏览器（关键步骤）
        pass
        # if self.browser:
        #     self.browser.quit()
        #     spider.logger.info("Chromium browser closed successfully.")
    def process_request(self, request, spider):
        def _process_request(request):
            wait_ele=request.meta.get('wait_ele', None)
            print("请求wait_ele",wait_ele)
            page =self.pool.get_page()
            try:
                page.get(request.url,timeout=15)
                if wait_ele:
                    page.wait.eles_loaded(wait_ele, timeout=5,any_one=True)
                html = page.html
                return HtmlResponse(
                    url=page.url,
                    body=html.encode('utf-8'),
                    request=request,
                    encoding='utf-8'
                )
            finally:
                self.pool.release_page(page)

        return threads.deferToThread(_process_request, request)
    

