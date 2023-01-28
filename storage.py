import json
from abc import ABC, abstractmethod

import pymongo.database

from mongo import MongoDatabase


class AbstractStorage(ABC):

    @abstractmethod
    def store(self, data, *args):
        pass

    @abstractmethod
    def load(self):
        pass


class MongoStorage(AbstractStorage):

    def __init__(self):
        self.mongo = MongoDatabase()

    def store(self, data, collection, *args):
        collection = getattr(self.mongo.database, collection)
        if isinstance(data, list) and len(data) > 1:
            collection.insert_many(data)
        else:
            collection.insert_one(data)

    def load(self, collection_name, filter_data=None):
        collection = self.mongo.database[collection_name]
        if filter_data is not None:
            data = collection.find(filter_data)
        else:
            data = collection.find()
        return data

    def update_flag(self, data):
        self.mongo.database.adv_links.find_one_and_update(
            {'_id': data['_id']},
            {'$set': {'flag': True}}
        )


class FileStorage(AbstractStorage):
    def store(self, data, filename, *args):
        if filename != 'adv_links':
            filename = data['post_id']
        with open(f'./fixtures/adv/{filename}.json', 'w') as f:
            f.write(json.dumps(data))

    def load(self):
        with open('fixtures/adv/adv_links.json', 'r') as f:
            links = json.loads(f.read())
        return links

    def update_flag(self, data):
        pass
