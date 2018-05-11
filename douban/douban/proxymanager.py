import requests
from redis import Redis


class ProxyManager:
    def __init__(self):
        self.redis = Redis()
        self.url = 'http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=458b3e0f10414a04b768c7e889e15813&count=10&expiryDate=0&format=2'

    def __download_proxies(self):
        # 下载代理地址，存储到redis
        r = requests.get(self.url).text
        if 'code' in r:
            return

        for proxy in r.splitlines():
            self.redis.sadd('proxy', proxy)
        self.redis.srem('proxy', '')  # 删除空条目

    def __get(self):
        proxy = self.redis.srandmember('proxy')
        while proxy is None:
            self.__download_proxies()
            proxy = self.redis.srandmember('proxy')

        return proxy.decode()

    def __delete(self, proxy):
        self.redis.srem('proxy', proxy)

    def __put(self, proxy):
        self.redis.sadd('proxy', proxy)

    def all(self):
        return self.redis.smembers('proxy')

    def get_http(self):
        return 'http://{}'.format(self.__get())

    def get_https(self):
        return 'https://{}'.format(self.__get())

    def delete_http(self, proxy):
        self.__delete(proxy[7:])

    def delete_https(self, proxy):
        self.__delete(proxy[8:])

    def put_http(self, proxy):
        self.__put(proxy[7:])

    def put_https(self, proxy):
        self.__put(proxy[8:])
