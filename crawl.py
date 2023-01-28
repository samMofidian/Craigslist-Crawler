import json
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from config import BASE_LINK, STORAGE_TYPE
from parsing import AdvertisementPageParser
from storage import MongoStorage, FileStorage


class CrawlerBase(ABC):

    def __init__(self):
        self.storage = self.__set_storage()

    @staticmethod
    def __set_storage():
        if STORAGE_TYPE == 'mongo':
            return MongoStorage()
        return FileStorage()

    @abstractmethod
    def start(self, store=False):
        pass

    @abstractmethod
    def store(self, data, filename=None):
        pass

    @staticmethod
    def get(url):
        try:
            response = requests.get(url)
        except requests.HTTPError:
            return None
        # print(response.status_code, response.url)
        return response


class LinkCrawler(CrawlerBase):

    def __init__(self, cities, link=BASE_LINK):
        self.cities = cities
        self.link = link
        super().__init__()

    def find_links(self, html_doc):
        bs = BeautifulSoup(html_doc, 'html.parser')
        return bs.find_all('a', attrs={'class': 'hdrlnk'})

    def start_crawl_city(self, url):
        start = 0
        crawl = True
        adv_links = list()
        while crawl:
            response = self.get(url+str(start))
            if response is None:
                crawl = False
                continue
            new_links = self.find_links(response.text)
            adv_links.extend(new_links)
            start += 120
            crawl = bool(len(new_links))

        return adv_links

    def start(self, store=False):
        adv_links = list()
        for city in self.cities:
            links = self.start_crawl_city(self.link.format(city))
            print(f"{city}\t\t total: {len(links)}")
            adv_links.extend(links)
        if store:
            self.store([{'url': li.get('href'), 'flag': False} for li in adv_links])
        return adv_links

    def store(self, data, *args):
        self.storage.store(data, 'adv_links')


class DataCrawler(CrawlerBase):

    def __init__(self):
        super().__init__()
        self.links = self.__load_links()
        self.parser = AdvertisementPageParser()

    def __load_links(self):
        return self.storage.load('adv_links', {'flag': False})

    def start(self, store=False):
        for link in self.links:
            response = self.get(link['url'])
            data = self.parser.parse(response.text)
            if store:
                self.store(data, data.get('post_id', 'sample'))

            self.storage.update_flag(link)

    def store(self, data, filename, *args):
        self.storage.store(data, 'adv_data')
        print(f'saving... {filename}')


class ImageCrawler(CrawlerBase):

    def __init__(self):
        super().__init__()
        self.advs = self.__load_advertisements()

    def __load_advertisements(self):
        return self.storage.load('adv_data')

    @staticmethod
    def get(url):
        try:
            response = requests.get(url, stream=True)
        except requests.HTTPError:
            return None
        # print(response.status_code, response.url)
        return response

    def start(self, store=True):
        for adv in self.advs:
            counter = 1
            for image in adv['images']:
                response = self.get(image['url'])
                if store:
                    self.store(response, adv['post_id'], counter)
                counter += 1

    def store(self, data, adv_id, image_number):
        filename = f'{adv_id}-{image_number}'
        return self.save_to_disk(data, filename)

    @staticmethod
    def save_to_disk(response, filename):
        with open(f'fixtures/images/{filename}.jpg', 'ab') as f:
            f.write(response.content)
            for _ in response.iter_content():
                f.write(response.content)

        print(filename)
        return filename

