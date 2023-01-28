from bs4 import BeautifulSoup


class AdvertisementPageParser:

    def __init__(self):
        self.bs = None

    @property
    def title(self):
        title_tag = self.bs.find('span', attrs={'id': 'titletextonly'})
        if title_tag:
            return title_tag.text
        return None

    @property
    def price(self):
        price_tag = self.bs.find('span', attrs={'class': 'price'})
        if price_tag:
            return price_tag.text
        return None

    @property
    def body(self):
        body_tag = self.bs.select_one('#postingbody')
        if body_tag:
            return body_tag.text
        return None

    @property
    def post_id(self):
        selector = 'p.postinginfo:nth-child(1)'
        id_tag = self.bs.select_one(selector)
        if id_tag:
            return id_tag.text.replace('post id: ', '')
        return None

    @property
    def created_time(self):
        selector = '.postinginfos > p:nth-child(2)'
        time_tag = self.bs.select_one(selector)
        # selector2 = '.postinginfos > p:nth-child(2) > time:nth-child(1)'
        # time_tag2 = self.bs.select_one(selector2)
        if time_tag:
            return time_tag.text.replace('posted: ', '')
            # return time_tag2.attrs['datetime']
        return None

    @property
    def modified_time(self):
        selector = 'p.postinginfo:nth-child(3)'
        modify_tag = self.bs.select_one(selector)
        if modify_tag:
            return modify_tag.text.replace('updated: ', '')
        return None

    @property
    def images(self):
        images_list = self.bs.find_all('img')
        images_sources = set([img.attrs['src'].replace('50x50c', '600x450') for img in images_list])
        return [{"url": src, "flag": False} for src in images_sources]

    def parse(self, html_data):
        self.bs = BeautifulSoup(html_data, 'html.parser')
        data = dict(
            title=self.title, price=self.price, body=self.body, post_id=self.post_id,
            created_time=self.created_time, modified_time=self.modified_time,
            images=self.images
        )

        return data




