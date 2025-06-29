# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from threading import Lock
from twisted.enterprise import adbapi
from copy import deepcopy, copy
import hashlib
import redis
from scrapy.exceptions import DropItem

class IncrementalPipeline:
    def __init__(self):
        # 初始化Redis连接（如果使用本地文件去重，可替换为文件操作）
        self.redis_conn = redis.Redis(host="redis", port=6379, db=7)
        


    # @classmethod
    # def from_crawler(cls, crawler):
    #     # 从Scrapy配置中读取Redis参数（如果未使用Redis，可跳过）
    #     return cls(
    #         redis_host=crawler.settings.get('REDIS_HOST'),
    #         redis_port=crawler.settings.get('REDIS_PORT')
    #     )

    def generate_fingerprint(self, item):
        """
        生成内容指纹的方法
        根据资讯的标题和发布时间生成唯一哈希值
        """
        # 示例：组合标题和发布时间作为唯一标识
        unique_str = f"{item['title']}{item['time']}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def process_item(self, item, spider):
        # 生成当前Item的指纹
        fingerprint = self.generate_fingerprint(item)
        self.redis_key = f"news_fingerprints:{spider.name}"
        # 检查指纹是否已存在
        if self.redis_conn.sismember(self.redis_key, fingerprint):
            raise DropItem(f"重复内容，跳过：{item['title']}")
        else:
            # 存储新指纹
            self.redis_conn.sadd(self.redis_key, fingerprint)
            return item  # 返回Item，继续后续处理


class EduNewsPipeline:
    def __init__(self):
        self.data_all = []
        self.lock = Lock()  # 线程安全锁
    def open_spider(self, spider):
        print("-----------数据库连接---------------")
        self.dbpool = adbapi.ConnectionPool(
            'pymysql', host='mysql',
            user='root', passwd='123456', db='test', charset='utf8'
        )
    
    def close_spider(self, spider):
        print("-----------数据库关闭---------------")
        if self.data_all:
            with self.lock:
                remaining = copy(self.data_all)
                self.data_all.clear()
                self.dbpool.runInteraction(self.insert_data, remaining)
                
        self.dbpool.close()

    def insert_data(self, cursor, data):
        print("-----------开始插入数据---------------")
        sql = "insert into edu_news(source_web_name,source_name,source_url,title,url,time,create_time) values(%s,%s,%s,%s,%s,%s,%s)"
        cursor.executemany(sql, data)
        print("-----------插入数据成功---------------")

    def _handle_error(self, failure, batch, spider):
        spider.logger.error(f"数据库插入失败: {failure.getTraceback()}")
        with self.lock:
            self.data_all.extend(batch)  # 失败数据重新入队

    def _retry_insert(self, data, retries=3):
        """失败重试机制"""
        for i in range(retries):
            try:
                self.dbpool.runInteraction(self._batch_insert, data)
                break
            except Exception as e:
                if i == retries-1:
                    raise
    def process_item(self, item, spider):
        print("-----------开始处理数据---------------")
        data=(
        item.get("source_web_name",""),
        item.get("source_name",""),
        item.get("source_url",""),
        item.get("title",""),
        item.get("url",""),
        item.get("time",""),
        item.get("create_time",""))


        with self.lock:
            self.data_all.append(data)
            if len(self.data_all) > 10:
                batch=deepcopy(self.data_all)
                self.data_all.clear()
                self.dbpool.runInteraction(self.insert_data, batch).addErrback(
                    self._handle_error, 
                    batch, 
                    spider
                )
                

        return item
