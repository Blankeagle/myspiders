# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class DefaultItemPipeline:
    def process_item(self, item, spider):
        item.setdefault('title', '')
        item.setdefault('author', '')
        item.setdefault('publisher', '')
        item.setdefault('publish_time', '0000-00-00')
        item.setdefault('tags', [])
        item.setdefault('page', 0)
        item.setdefault('original_price', 0.0)
        item.setdefault('star', 0.0)
        item.setdefault('comment_cnt', 0)
        return item


class MongoPipeline:
    collection_name = 'book'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'douban')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
