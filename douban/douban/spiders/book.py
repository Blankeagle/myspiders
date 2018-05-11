from douban.items import BookItemLoader
from scrapy import Spider, Request
import re
from scrapy_redis.spiders import RedisSpider
class Book(RedisSpider):
    name = 'douban-book'
    #start_urls = ['https://book.douban.com/tag/']
    allowed_domains = ['douban.com']

    def parse(self, response):
        for tag in response.xpath('//a').re('/tag/(.*?)"'):
            url = '/tag/{}'.format(tag)
            yield response.follow(url, callback=self.parse_tag)

    def parse_tag(self, response):
        book_xpath = '//div[@class="info"]/h2/a/@href'
        for book_url in response.xpath(book_xpath).extract():
            yield Request(book_url, callback=self.parse_book)

        next_xpath = '//*[@class="next"]/a/@href'
        for href in response.xpath(next_xpath):
            yield response.follow(href, callback=self.parse_tag)

    def parse_book(self, response):
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
        loader.add_value('comments','bitch')
        # yield loader.load_item()
        comments_page = response.xpath('//h2/span[@class="pl"]/a/@href').extract_first()
        try:
            yield Request(comments_page,
                      callback=self.parse_comment,
                      meta={'loader': loader.load_item(),'list1':list()}
                      )
        except:
            print('no comments')
            loader.add_value('comments', 'no comments')
            yield loader.load_item()
        # yield loader.load_item()

    def parse_comment(self, response):
        loader = response.meta['loader']
        list1 = response.meta['list1']

        page_comments = response.xpath('//div[@class="comment"]').extract()

        for page_comment in page_comments:
            #print(page_comment)
            try:
                dict1 = {}
                dict1['date'] = re.findall(r'span>(\d+.*\d+)', page_comment)[0]
                comment=re.findall(r'content">(.*)', page_comment)[0]
                comment=comment.split('</p>')[0]
                dict1['comment'] = comment
                dict1['stars'] = re.findall(r'allstar(\d)', page_comment)[0]

            except:
                continue

            list1.append(dict1)
        nextcomments_page= response.xpath("//*[contains(text(),'后一页')]/@href").extract_first()

        if nextcomments_page == None:
            # print(list1)
            print(len(list1))
            # print(response.url)
            loader['comments']= list1
            yield loader
        else:
            try:
                yield response.follow(nextcomments_page,
                           callback=self.parse_comment,
                           meta={'loader': loader, 'list1': list1})
            except:
                print(nextcomments_page)

