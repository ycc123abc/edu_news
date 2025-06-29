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
from threading import Lock
from scrapy import signals
from twisted.internet import threads
from DrissionPage import Chromium, ChromiumOptions
from scrapy.http import HtmlResponse
from queue import Queue
from threading import Lock
from scrapy import signals
from twisted.internet import threads

class PagePool:
    def __init__(self, pool_size=8):
        self.pool_size = pool_size
        self.chromium_options = ChromiumOptions()
        self.chromium_options.no_imgs(True)
        self.chromium_options.set_argument('--disable-blink-features=AutomationControlled')
        self.chromium_options.headless()
        self.chromium_options.set_argument('--no-sandbox')
        self.chromium_options.set_argument("--disable-gpu")
        self.browser = Chromium(self.chromium_options)
        self.pages = Queue()
        self.max_pool_size = 2 * self.pool_size
        self.total_pages = 0
        self.pool_lock = Lock()
        for _ in range(pool_size):
            tab = self.browser.new_tab()
            tab.set.user_agent(tab.user_agent.replace('Headless', ''))
            self.pages.put(tab)
            self.total_pages += 1

    def get_page(self):
        if self.pages.empty() and self.total_pages < self.max_pool_size:
            with self.pool_lock:
                if self.pages.empty() and self.total_pages < self.max_pool_size:
                    tab = self.browser.new_tab()
                    tab.set.user_agent(tab.user_agent.replace('Headless', ''))
                    self.total_pages += 1
                    return tab
        return self.pages.get()

    def release_page(self, page):
        page.get("about:blank")
        self.pages.put(page)

class DrissionpageMiddleware:
    _shared_pool = None
    _active_spiders = 0
    _lock = Lock()

    def __init__(self, pool_size=8):
        cls = self.__class__
        with cls._lock:
            if cls._shared_pool is None:
                cls._shared_pool = PagePool(pool_size)
            self.pool = cls._shared_pool
            cls._active_spiders += 1

    @classmethod
    def from_crawler(cls, crawler):
        pool_size = crawler.settings.getint('CONCURRENT_REQUESTS', 8)
        middleware = cls(pool_size)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        def _process_request(request):
            wait_ele = request.meta.get('wait_ele', None)     #等待谁出现
            change=request.meta.get('change', False)            #是否切换模式
            page = self.pool.get_page()
            try:
                if change:
                    page.change_mode()
                    page.get(request.url)
                    html=page.html
                    page.change_mode()
                else:
                    page.get(request.url)
                    page.wait(0.1)
                    if wait_ele:
                        page.wait.eles_loaded(wait_ele, timeout=10, any_one=True)
                    html = page.html.encode('utf-8')
                return HtmlResponse(
                    url=page.url,
                    body=html,
                    request=request,
                    encoding='utf-8'
                )
            finally:
                self.pool.release_page(page)

        return threads.deferToThread(_process_request, request)

    def spider_closed(self, spider):
        cls = self.__class__
        with cls._lock:
            cls._active_spiders -= 1
            if cls._active_spiders == 0 and cls._shared_pool is not None:
                cls._shared_pool.browser.quit()
                cls._shared_pool = None
                spider.logger.info("Chromium browser closed successfully.") 