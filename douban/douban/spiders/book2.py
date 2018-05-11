from scrapy.linkextractors import LinkExtractor as SLE
from scrapy.spiders import CrawlSpider, Rule

from douban.items import BookItemLoader


class Book(CrawlSpider):
    name = 'douban-book2'
    allowed_domains = ["douban.com"]
    start_urls = ['https://book.douban.com/tag/']

    rules = [
        Rule(SLE(allow=(r'/subject/\d+$',)), callback='parse_subject'),
        Rule(SLE(allow=('/tag/[^/]+$',)))
    ]

    def parse_subject(self, response):
        loader = BookItemLoader(selector=response)
        loader.add_xpath('title', '//*[@property="v:itemreviewed"]/text()')
        loader.add_xpath('star', '//*[@property="v:average"]/text()')
        loader.add_xpath('comment_cnt', '//*[@property="v:votes"]/text()')

        info_xpath = {
            'author': [".//*[contains(text(), ' 作者')]/following-sibling::a/text()",
                       ".//*[contains(text(), '作者:')]/following-sibling::a/text()"],
            'publisher': [".//*[contains(text(), '出版社:')]/following-sibling::text()[1]"],
            'publish_time': [".//*[contains(text(), '出版年:')]/following-sibling::text()[1]"],
            'page': [".//*[contains(text(), '页数:')]/following-sibling::text()[1]"],
            'original_price': [".//*[contains(text(), '定价:')]/following-sibling::text()[1]"],
        }
        info = response.xpath('//*[@id="info"]')
        loader.selector = info
        for k, v in info_xpath.items():
            for w in v:
                loader.add_xpath(k, w)

        tags = response.xpath("//*[@id='db-tags-section']")
        loader.selector = tags
        loader.add_xpath('tags', './/a/text()')

        yield loader.load_item()
