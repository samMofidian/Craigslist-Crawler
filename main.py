import sys
from crawl import LinkCrawler, DataCrawler, ImageCrawler


# def get_pages_data():
#     raise NotImplementedError


if __name__ == '__main__':
    switch = sys.argv[1]
    if switch == 'find_links':
        crawler = LinkCrawler(cities=['berlin'])
        crawler.start(store=True)
    elif switch == 'extract_pages':
        crawler = DataCrawler()
        crawler.start(store=True)
    elif switch == 'download_images':
        crawler = ImageCrawler()
        crawler.start(store=True)
