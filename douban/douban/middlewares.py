# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
from douban.user_agents import user_agent
from douban.proxymanager import ProxyManager
from string import ascii_letters, digits
import logging
log = logging.getLogger('ProxyMiddleware')


# class UserAgentMiddleware:
#     def process_request(self, request, spider):
#         agent = random.choice(agents)
#         request.headers['User-Agent'] = agent


# class CookieMiddleware:
#     def process_request(self, request, spider):
#         random_bid = ''.join(random.sample(ascii_letters+digits, 11))
#         radmon_ll = random.randint(100000, 200000)
#         request.cookies['ll'] = "'{}'".format(radmon_ll)
#         request.cookies['bid'] = random_bid


class ProxyMiddleware:
    def __init__(self):
        self.proxy_manager = ProxyManager()

    def process_request(self, request, spider):
        if 'proxy' in request.meta:  # 已经设置过代理，表明该代理不可用，删除之
            self.proxy_manager.delete_https(request.meta['proxy'])
        # 设置代理
        request.meta['proxy'] = self.proxy_manager.get_https()

    def process_response(self, request, response, spider):
        # 执行到这儿表示响应是正常的
        self.proxy_manager.put_https(request.meta['proxy'])
        return response

    def process_exception(self, request, exception, spider):
        # 连接代理异常
        return request.replace(dont_filter=True)


class DoubanMiddleware:
    def process_request(self, request, spider):
        # UA
        request.headers['User-Agent'] = user_agent()

        # COOKIE
        random_bid = ''.join(random.sample(ascii_letters+digits, 11))
        radmon_ll = random.randint(100000, 200000)
        request.cookies['ll'] = "'{}'".format(radmon_ll)
        request.cookies['bid'] = random_bid

    def process_response(self, request, response, spider):
        # 豆瓣301是一个页面正常跳转
        if response.status == 301:
            return request.replace(url=response.headers['Location'].decode())

        # 处理被ban的情况
        if '豆瓣读书' not in response.text:
            log.info('BAD: {} {} {} {}'.format(
                response.status, request.url,
                response.text, request.meta['proxy']))

            return request.replace(dont_filter=True)

        return response
