# coding:utf-8
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import ast
import requests
from bs4 import BeautifulSoup
import database
import time
import multiprocessing

head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"}
db = database.Mysql(
    '127.0.0.1',
    'root',
    'Mroot@123',
    3306,
    'mayi_news',
    'utf8')[0]


def get_soup(url):
    data = requests.get(url, headers=head).content
    soup = BeautifulSoup(data, 'lxml')
    return soup


def verify_url(news_url):
    sql = "select url from news_tb where url='%s';" % news_url
    result = db.select_data(sql)
    if result == ():
        return False
    else:
        return True


def get_guonei():
    url = "http://temp.163.com/special/00804KVA/cm_guonei.js?callback=data_callback"
    response = requests.get(url).content.decode('gbk')
    data = response[14:-1:]
    ast_data = ast.literal_eval(data)
    for i in ast_data:
        url = i.get('docurl')
        if verify_url(url):
            continue
        title = i.get('title')
        soup = get_soup(url)
        div_data = soup.find_all('div', {'class': "post_text"})
        video = div_data[0].find_all('param', {'name': 'movie'})
        video_url = ''
        if video:
            for i in video:
                video_url += (i.get('value') + '\n')
        if div_data:
            p_data = div_data[0].find_all('p')
            content = ''
            img_url = ''
            for i in p_data:
                script_data = i.find_all('script')
                if script_data:
                    continue
                img_data = i.find_all('img')
                if img_data:
                    img_url += (img_data[0].get('src') + '\n')
                    continue
                if i.find_all('style') or i.find_all('a') or i.select('img'):
                    continue
                line = i.get_text()
                if line:
                    content += (line + '\n')
            operator = 'liuxiaodong'
            classes = 1
            state = 0
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql = "insert into news_tb(title,create_time,content,img,video,operator," \
                  "url,classes,state) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            db.change_data(
                sql,
                (title,
                 create_time,
                 content,
                 img_url,
                 video_url,
                 operator,
                 url,
                 classes,
                 state))
            print 1,

def get_yule():
    soup = get_soup(
        'http://news.163.com//special//0001386F//rank_ent.html')
    data_1 = soup.find_all('div', {"class": "tabContents active"})
    for i in data_1[0].select('td > a'):
        title = i.string
        url = i.get('href')
        if verify_url(url):
            continue
        soup_each = get_soup(url)
        data_1_each = soup_each.select('#endText')
        if not data_1_each:
            continue
        img = data_1_each[0].select('p.f_center > img')
        video = data_1_each[0].find_all('param', {'name': 'movie'})
        img_url = ''
        video_url = ''
        content = ''
        if img:
            for i in img:
                img_url += (i.get('src') + '\n')
        if video:
            for i in video:
                video_url += (i.get('value') + '\n')
        for j in data_1_each[0].select('p'):
            if j.find_all('style') or j.find_all('a') or j.select('img'):
                continue
            if j.find_all('b'):
                if j.get_text().find("报道") != -1:
                    content += (j.get_text().split(j.find_all('b')
                                                   [0].string, 1)[1] + '\n')
                else:
                    content += (j.get_text() + '\n')
            else:
                content += (j.get_text() + '\n')
        c_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if content.strip():
            sql = "insert into news_tb(title,create_time,content,img,video,operator,url,classes) values(%s,%s,%s,%s,%s,%s,%s,%s)"
            db.change_data(
                sql,
                (title,
                 c_time,
                 content,
                 img_url,
                 video_url,
                 'guosiyuan',
                 url,
                 5))
            print 5,


class Get_keji(object):
    def __init__(self):
        self.url = 'http://news.163.com/special/0001386F/rank_tech.html'
        self.headers = head
        self.title_url_dict = {}

    def parse_url(self, url):
        res = requests.get(url, headers=self.headers).content
        soup = BeautifulSoup(res, 'lxml')
        return soup

    def get_url(self, soup):  # 获取title和url

        div_data = soup.find_all('div', {'class': "tabContents active"})
        a_data = div_data[0].find_all('a')
        for i in a_data:
            title = i.string
            link = i.get('href')
            self.title_url_dict[title] = link
        return self.title_url_dict

    def download_text(self, url):  # 获取文本
        text_list = []
        soup = self.parse_url(url)
        div_data = soup.find_all('div', {'class': "post_text"})
        p_data = div_data[0].find_all('p')
        for i in p_data:
            if i.select('b'):
                continue
            content = i.get_text()
            pos = content.find('日消息'.decode('utf-8'))
            if pos > 0:
                content = content[pos + 4:-1]
                text_list.append(content)
        text_list = [i for i in text_list if i != '']
        return '\n'.join(text_list)

    def get_picture_url(self, url):  # 获取图片地址

        soup = self.parse_url(url)
        p_data = soup.find_all('p', {'class': "f_center"})
        re_src = r'src="(.+?)"'
        src_url = re.findall(re_src, str(p_data))
        return '\n'.join(src_url)

    def write_database(self):

        write_time = time.strftime('%Y-%m-%d %X')
        operator1 = 'lisen'
        do_main1 = 4
        state1 = 0
        soup = self.parse_url(self.url)
        title_url_dict = self.get_url(soup)
        for title, url in title_url_dict.items():
            if db.select_data("select url from news_tb where url='%s'" % url):
                continue
            text = self.download_text(url)
            pic_url = self.get_picture_url(url)
            if text.strip('\n'):
                sql = "insert into news_tb(title,create_time,content,img,operator,url,classes,state)" \
                      "values(%s,%s,%s,%s,%s,%s,%s,%s)"
                try:
                    db.change_data(
                        sql,
                        (title,
                         write_time,
                         text,
                         pic_url,
                         operator1,
                         url,
                         do_main1,
                         state1))
                    print 4,
                except BaseException:
                    pass

    def run(self):
        self.write_database()


def get_tiyu():
    url = "http://news.163.com/special/0001386F/rank_sports.html"
    soup = get_soup(url)
    code_data = soup.find_all('div', {'class': "tabContents active"})
    tbody_data = code_data[0].find_all('a')
    for i in tbody_data:
        url_1 = i.get('href')
        if verify_url(url_1):
            continue
        data_soup = get_soup(url_1)
        name = data_soup.find_all('h1')
        try:
            name = name[0].string
        except BaseException:
            continue
        data_1 = data_soup.find_all('div', {'class': "post_text"})
        if not data_1:
            continue
        cc_url = data_1[0].find_all('img', {'alt': name})
        png = ""
        value_vVurl = ""
        for i in cc_url:
            png += i.get('src') + '\n'
        video = data_1[0].find_all('div', {'class': "video-inner"})
        if video:
            for i in video:
                value_url = video[0].find_all('param', {'name': "movie"})[
                    0].get('value')
                value_vVurl += (value_url + '\n')
        matter = ""
        for i in data_1[0].find_all('p'):
            if i.find_all('style') or i.find_all('span') or i.find_all('img'):
                continue
            matter += i.get_text() + '\n'
        pos = matter.find("本文来源：")
        if pos > 0:
            matter = matter[0:pos]
        pos_1 = matter.find('日报道：')
        if pos_1 > 0:
            matter = matter[pos_1 + 4:-1]
        time = datetime.datetime.now().strftime('%Y-%m-%d %X')
        operator = 'liyongan'
        do_main = 2
        order_id = 0
        state = 0
        if matter.strip('\n'):
            sql = "insert into news_tb(title,create_time,content,img,video,operator,url,classes,order_id,state) values" \
                  "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            db.change_data(
                sql,
                (name,
                 time,
                 matter,
                 png,
                 value_vVurl,
                 operator,
                 url_1,
                 do_main,
                 order_id,
                 state))
            print 2,

def get_guoji():
    url = 'http://temp.163.com//special//00804KVA//cm_guoji.js?callback=data_callback'
    all_data = requests.get(url, headers=head).content
    all_data = ast.literal_eval(all_data[14:-1:])
    for i in all_data:
        news_url = i["docurl"]
        if verify_url(news_url):
            continue
        title = i['title'].decode('gbk')
        soup = get_soup(news_url)
        div_data = soup.find_all('div', {'class': 'post_text'})
        p_data = div_data[0].find_all('p')
        text_list = ''
        for i in p_data:
            if i.find_all('style') or not i.get_text():
                continue
            text_list += (i.get_text() + '\n')
        video_url = ''
        img = div_data[0].select('p.f_center')
        video = div_data[0].find_all('param', {'name': 'movie'})
        jpg_urls = ''
        if img:
            jpg_list = []
            for each_data in div_data:
                re_jpg = 'src="(.+?)"'
                jpg_url = re.findall(re_jpg, str(each_data))
                jpg_list.append(jpg_url[0])
            jpg_urls = '\n'.join(jpg_list)
        if video:
            for i in video:
                video_url += (i.get('value') + '\n')
        time_data = time.strftime('%Y-%m-%d %X')
        operator = 'dongzhanwu'
        do_main = 3
        sql = "insert into news_tb(title,content,img,video,url,create_time,operator,classes) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        db.change_data(
            sql,
            (title,
             text_list,
             jpg_urls,
             video_url,
             news_url,
             time_data,
             operator,
             do_main))
        print 3,

 
def get_keji():
    news = Get_keji()
    news.run()


def spider_run():
    function_list = [get_keji, get_guoji, get_tiyu, get_yule, get_guonei]
    pool = multiprocessing.Pool(processes=3)
    for i in function_list:
        pool.apply_async(i, ())
    pool.close()
    pool.join()


if __name__ == '__main__':
    spider_run()
