from urllib import request
import re
import time
import random
import sys
import pymysql
from hashlib import md5
from fake_useragent import UserAgent
import threading


class FilmSkySpider(object):
    def __init__(self):
        self.url = 'https://www.dytt8.net/html/gndy/dyzz/list_23_{}.html'
        self.db = pymysql.connect('localhost', 'root', '123456', 'filmskydb', charset='utf8')
        self.cursor = self.db.cursor()

    # 请求 - 功能函数
    def get_html(self, url):
        ua = UserAgent()
        headers = {'User-Agent': ua.random }
        req = request.Request(url=url, headers=headers)
        res = request.urlopen(req)
        html = res.read().decode('gb2312', 'ignore')

        return html

    # 解析 - 功能函数
    def re_func(self, re_bds, html):
        pattern = re.compile(re_bds, re.S)
        r_list = pattern.findall(html)

        return r_list

    # 真正提取数据的函数
    def parse_html(self, one_url, num):
        print('第{}页正在爬取'.format(num))
        one_html = self.get_html(one_url)
        re_bds = r'<table width="100%".*?<td width="5%".*?<a href="(.*?)".*?ulink">.*?</table>'
        # link_list: ['/html/xxx','/html/yyy']
        # https://www.dytt8.net
        link_list = self.re_func(re_bds, one_html)
        # link_list = ['https://www.dytt8.net' + url for url in link_list]
        for link in link_list:
            # 判断是否需要爬取此链接
            # 1.获取指纹
            two_url = 'https://www.dytt8.net' + link
            s = md5()
            s.update(two_url.encode())
            finger = s.hexdigest()
            # print(finger,type(finger))
            # 2.通过函数判断指纹在数据库中是否存在
            if self.is_go_on(finger):
                # 1. 爬
                self.save_html(two_url)
                # 2. 把指纹存入到数据库
                ins = 'insert into request_finger values (%s)'
                # print(1111)
                self.cursor.execute(ins, args=(finger.strip("'")))
                self.db.commit()
            else:
                sys.exit('更新完成')
        print('第{}页爬取成功'.format(num))

    # 判断是否需要抓取该链接
    def is_go_on(self, finger):
        sel = 'select finger from request_finger where finger = (%s)'
        # execute 方法返回为数字 0 或者 非0(字段条数)
        n = self.cursor.execute(sel, [finger])
        # print(n, type(n))
        if not n:
            return True

    # 真正获取名称和下载链接的函数
    def save_html(self, two_url):
        two_html = self.get_html(two_url)
        re_bds = r'<div class="title_all"><h1><font color=#07519a>(.*?)</font></h1></div>.*?<td style="WORD-WRAP.*?>.*?>(.*?)</a>'
        # film_list = [('name','downloadlink')]
        film_list = self.re_func(re_bds, two_html)
        # 插入数据库
        ins = 'insert into filmtab(name,download) values(%s,%s)'
        # args 参数可以是列表和元祖
        L = list(film_list[0])
        # print(L)
        self.cursor.execute(ins, args=L)
        self.db.commit()

    def run(self):
        # thread_list = []
        for i in range(1, 203):
            url = self.url.format(i)
            self.parse_html(url, i)
            # thread = threading.Thread(target=self.parse_html, args=[url, i+1])
            # thread_list.append(thread)
            # thread.start()

        # for thread in thread_list:
        #     thread.join()


if __name__ == '__main__':
    spider = FilmSkySpider()
    spider.run()

























