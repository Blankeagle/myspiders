# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re

from scrapy import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Identity, TakeFirst


class BookItem(Item):
    title = Field()
    author = Field()
    publisher = Field()
    publish_time = Field()
    tags = Field()
    page = Field()
    original_price = Field()
    star = Field()
    comment_cnt = Field()
    comments = Field()


def remove_dup_space(data):
    return ' '.join(data.split())


def format_date(date):
    '''
    时间为字符串格式:1990-2-1
    若缺失月份，则返回格式为1990-00
    '''
    d = re.compile(r'\d+')
    ymd = d.findall(date)
    length = len(ymd)
    if length == 0 or len(ymd[0]) > 4:
        return '0000-00-00'
    elif length == 1:
        return '{}-00-00'.format(ymd[0])
    elif length == 2:
        return '{}-{}-00'.format(ymd[0], ymd[1].zfill(2))
    elif length == 3:
        return '{}-{}-{}'.format(ymd[0], ymd[1].zfill(2), ymd[2].zfill(2))


def format_page(page):
    try:
        return int(''.join(filter(str.isdigit, page)))
    except:
        return 0


def format_price(price):
    # 尝试匹配浮点数 12.34元
    p = re.findall(r'\d+.\d+', price)
    # 匹配浮点数失败，尝试匹配整数 12元
    if p == []:
        p = re.findall(r'\d+', price)

    try:
        return float(p[0])
    except:
        # 价格非数字，比如:非卖品. 返回0
        return 0.0


def format_star(star):
    try:
        return float(remove_dup_space(star))
    except:
        return 0.0


def format_comment_cnt(comment_cnt):
    try:
        return int(remove_dup_space(comment_cnt))
    except:
        return 0


class BookItemLoader(ItemLoader):
    default_item_class = BookItem
    default_output_processor = Compose(TakeFirst(), remove_dup_space)
    publish_time_out = Compose(TakeFirst(), remove_dup_space, format_date)
    tags_out = Identity()
    page_out = Compose(TakeFirst(), format_page)
    original_price_out = Compose(TakeFirst(), format_price)
    star_out = Compose(TakeFirst(), format_star)
    comment_cnt_out = Compose(TakeFirst(), format_comment_cnt)
    comments = Identity()
