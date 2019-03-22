# coding:utf-8
import urllib.request
import re
from bs4 import BeautifulSoup
import random
import requests
import lxml
import os
#from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
import time

my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]


def header(referer):
    headers = {
        'Host': 'i.meizitu.net',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(referer),
    }
    return headers


def url_open(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', random.choice(my_headers))
    req.add_header('Referer', 'http://www.umei.cc')
    try:
        response = urllib.request.urlopen(req, timeout=8.0).read().decode('utf-8')
    except Exception as e:  # 捕获异常
        return str(e)
    else:
        return response


def downloadUmei(suolue_index):
    suolue_index_temp = suolue_index
    img_num = 0  # 定义该缩略图下的图片数量
    img_fail_num = 0
    img_already_save_num = 0
    fail_times = 0
    while True:  # 得到大图页面下的所有图片
        res = url_open(suolue_index_temp)  # 请求缩略图地址获得大图页面

        if (res == 'HTTP Error 404: Not Found'):  # 如果返回404则所有图片均已遍历
            try:
                print('*: 图集【{}】共{}张图片，已保存{}张，新保存{}张 ,失败{}张'.format(src_name[0], img_num, img_num - img_fail_num,
                                                                img_num - img_fail_num - img_already_save_num,
                                                                img_fail_num))
            except Exception as e:
                print(e)
            break
        elif (res == '<urlopen error timed out>'):  # 超时
            print('!: 连接超时已跳过该图集')
            break
        else:
            imghtml = lxml.etree.HTML(res)
            src_data = imghtml.xpath('//*[@class="ImageBody"]/p/a/img/@src')  # 大图页的图片地址
            src_name = imghtml.xpath('//*[@class="ImageBody"]/p/a/img/@alt')  # 图片名字

            if (len(src_data) != 1):  # 失败图片
                if (fail_times < 5):  # 如果尝试次数小于5次
                    print('!: 图片 {} 下载失败 (未获取到地址),尝试第 {} 次'.format(img_num, fail_times + 1))
                    fail_times = fail_times + 1
                    continue
                else:
                    img_fail_num = img_fail_num + 1
                    print('!: 图片 {} 下载失败 (未获取到地址)'.format(img_num))
            else:
                pic_name = src_name[0] + '_' + str(img_num)  # 使用缩略图序号+页面号命名
                img_path = dir_path + str(src_name[0]) + '_' + pic_name + '.jpg'
                if os.path.isfile(img_path):
                    img_already_save_num = img_already_save_num + 1
                    print('*: 图片 {} 已经存在，已跳过'.format(pic_name))
                else:
                    try:  # 尝试下载
                        img_data = requests.get(src_data[0], timeout=10)  # 下载图片
                    except Exception as e:  # 下载超时
                        img_fail_num = img_fail_num + 1
                        print('!: 图片 {} 下载失败 (下载超时)'.format(pic_name))
                    else:  # 下载成功则保存
                        with open(img_path, 'wb')as f:
                            f.write(img_data.content)
                            print("*: 图片 {} 保存成功".format(pic_name))
                            f.close()
            img_num = img_num + 1  # 图片数量加1
            fail_times = 0
            suolue_index_temp = suolue_index[:-4] + '_%d.htm' % (img_num + 1)  # 更新大图url


def downloadMzitu(url):
    sel = lxml.etree.HTML(requests.get(url).content)
    # 图片总数
    total = sel.xpath('//div[@class="pagenavi"]/a[last()-1]/span/text()')[0]
    # 标题
    title = sel.xpath('//h2[@class="main-title"]/text()')[0]
    n = 1
    for i in range(int(total)):
        # 每一页
        try:
            link = '{}/{}'.format(url, i + 1)
            s = lxml.etree.HTML(requests.get(link).content)
            jpgLink = s.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
            filename = title + '_' + str(n) + '.jpg'
            file_path = dir_path +  filename
            if os.path.isfile(file_path):
                print('*: 图片 {} 已经存在，已跳过'.format(filename))
            else:
                print(u'图片 %s_%s 保存成功' % (title, n))
                with open(file_path, "wb+") as jpg:
                    jpg.write(requests.get(jpgLink, headers=header(jpgLink)).content)
            n += 1
        except Exception as e:
            print(e)


def get_url(num):  # 得到优美图库的详情页序列
    tag = 'yongzhuang'
    url = 'http://www.umei.cc'  # 需要设置首页地址
    page_index = url + '/tags/' + tag + '_' + str(num) + '.htm'
    response = url_open(page_index)  # 打开每一页图片
    html = lxml.etree.HTML(response)
    suolue_url = html.xpath('/html/body/div[2]/div[7]/ul/li/a/@href')
    return suolue_url


def get_page(pageNum):  # 获取妹子图主页列表
    baseUrl = 'http://www.mzitu.com/page/{}'.format(pageNum)
    selector = lxml.etree.HTML(requests.get(baseUrl).content)
    urls = []
    for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        urls.append(i)
    return urls


def get_usr_define():
    password_list = ['000000', '101010', '202020', '303030', '981017']
    usr_call = ['死一边去的', '可爱的', '尊敬的', '尊贵无比的', '亲爱的']
    usr_name = ['【普通会员】', '【黄金会员】', '【白金会员】', '【超级会员】', '【**可爱】']

    img_org_list = [False, True, True, True, True]
    download_speed_list = [1, 1, 10, 10, 10]
    download_page_list = [2, 2, 40, 40, 40]
    print('=======================================================')
    print('=                     人工智障爬虫                    =')
    print('=======================================================')
    print('*: 本程序用户分为[普通会员] [黄金会员] [白金会员] [超级会员]',end='\n\n')
    print('其功能区分如下表所示:',end='\n\n')

    print('| 【////\\\\\\\\】\t【普通会员】\t【黄金会员】\t【白金会员】\t【超级会员】|\t\n'
          '| 【图 片 源】\t[普通妹子]\t[精选妹子]\t[精选妹子]\t[精选妹子]  |\t\n'
          '| 【下载速度】\t[龟速下载]\t[龟速下载]\t[急速下载]\t[急速下载]  | \t\n'
          '| 【下载数量】\t[只有一页]\t[只有一页]\t[只有一页]\t[没有限制]  | \t\n')

    print('!: 请输入6位识别码以确认身份: ', end='')
    input_num = input()
    try:
        usr_id = password_list.index(input_num)
    except Exception as e:
        print('未输入正确识别码，将以[普通会员]身份运行!')
        usr_id = 0
        time.sleep(1)

    else:
        print('!: {}{}：图片将保存在{},请尽情欣赏！'.format(usr_call[usr_id], usr_name[usr_id], dir_path))
        if usr_id > 1:
            print('!: 为您开启急速下载中...')
        else:
            pass
        time.sleep(2)
    img_org = img_org_list[usr_id]
    download_speed = download_speed_list[usr_id]
    download_page = download_page_list[usr_id]
    return img_org, download_speed, download_page


if __name__ == '__main__':
    dir_path = 'D:/MyImg/'
    if (not os.path.exists(dir_path)):
        os.makedirs(dir_path)
    else:
        pass
    mul_url = []
    img_org, download_speed, download_page = get_usr_define()  # 获得用户权限
    print('!: 初始化页面资源中...')
    if (img_org == True):
        for i in range(1, download_page):
            mul_url.append(get_page(i))
        for i in range(0, download_page):
            with ThreadPool(download_speed) as pool:
                pool.map(downloadMzitu, mul_url[i])
    else:
        for i in range(1, download_page):
            mul_url.append(get_url(i))
        for i in range(0, download_page):
            with ThreadPool(download_speed) as pool:
                pool.map(downloadUmei, mul_url[i])
    print('恭喜！所有页面均已爬完~')
