import pymongo
from scrapy import log
from scrapy.exceptions import DropItem


class MongoPipeline(object):
    collection_name = 'govmon'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        d = dict(item)
        cursor = self.db.get_collection(self.collection_name).find({'link': d['link']})
        if cursor.count() == 0:
            log.msg('New Entry', level=log.DEBUG, spider=spider)
            d['version'] = 0
        else:
            last_revision = cursor[cursor.count() - 1]
            if last_revision['title'] == item['title'] \
                    and last_revision['text'] == item['text'] \
                    and last_revision['last_updated'] == item['last_updated'] \
                    and last_revision['file_urls'] == item['file_urls']:
                raise DropItem("Item not changed: %s" % item['link'])
            log.msg('New Version', level=log.DEBUG, spider=spider)
            d['version'] = cursor.count()
        self.db[self.collection_name].insert(d)
        return item
