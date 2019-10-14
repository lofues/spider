from urllib import request
import time
import random
import re
import os

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50'
]


class MaoyanSpider(object):
    def __init__(self):
        self.url = 'https://maoyan.com/board/4?offset={}'

    # 请求功能函数 - html
    def get_html(self, url):
        headers = {
            'User-Agent': random.choice(user_agents)
        }
        req = request.Request(url=url,
                                     headers=headers)
        res = request.urlopen(req)
        html = res.read().decode()

        return html

    # 解析功能函数
    def re_func(self, re_bds, html):
        pattern = re.compile(re_bds, re.S)
        r_list = pattern.findall(html)

        return r_list

    # 解析一级页面
    def parse_html(self, one_url):
        one_html = self.get_html(one_url)
        re_bds = r'.*?class="name"><a href="(.*?)" title="(.*?)".*?class="star">(.*?)</p>.*?上映时间：(.*?)</p>'

        # r_list: [('/films/1203','name','star'), ()]
        r_list = self.re_func(re_bds, one_html)

        print(r_list)
        self.save_html(r_list)

    # 解析二级页面
    def save_html(self, r_list):
        item = {}
        # r: ('/films/1203','name','star','time')
        for r in r_list:
            item['name'] = r[1].strip()
            item['star'] = r[2].strip()[3:]
            item['time'] = r[3].strip()[0:10]
            print(item['time'])
            two_link = 'https://maoyan.com' + r[0]
            self.save_image(two_link, item['name'])
            item['comment'] = self.get_comment(two_link)
            print(item)

    # 获取评论的函数
    def get_comment(self, two_link):
        two_html = self.get_html(two_link)
        re_bds = '<div class="comment-content">(.*?)</div>'
        comment_list = self.re_func(re_bds, two_html)

        return comment_list

    # 保存图片函数
    def save_image(self, two_link, name):
        two_html = self.get_html(two_link)
        re_bds = '<img class="default-img" data-src="(.*?)" alt="">'
        # link_list: ['http://xx.jpg',]
        link_list = self.re_func(re_bds, two_html)
        # print(link_list)

        # 创建对应文件夹
        directory = '/home/tarena/images/{}/'.format(name)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 存储每个电影的图片
        print(link_list)
        for link in link_list:
            headers = {'User-Agent': random.choice(user_agents)}
            req = request.Request(url=link, headers=headers)
            res = request.urlopen(req)
            html = res.read()

            filename = directory + link.split('@')[0][-10:]
            with open(filename, 'wb') as f:
                f.write(html)
                print('file save ok')

    def run(self):
        for offset in range(0, 21, 10):
            url = self.url.format(offset)
            self.parse_html(url)


if __name__ == '__main__':
    spider = MaoyanSpider()
    spider.run()













