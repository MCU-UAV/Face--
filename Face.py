# coding:utf-8
import urllib.request
import re
from bs4 import BeautifulSoup
import random
import requests
import lxml
import os
import ctypes,sys
import base64
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

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# Windows CMD命令行 字体颜色定义 text colors
FOREGROUND_DARKGRAY = 0x08 # dark gray.
FOREGROUND_GREEN = 0x0a # green.
FOREGROUND_RED = 0x0c # red.
FOREGROUND_YELLOW = 0x0e # yellow.
FOREGROUND_BLUE = 0x09 # blue.

# get handle
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool


# reset white
def resetColor():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)


def color_print(mess,color):
    set_cmd_text_color(color)
    print(mess)
    resetColor()


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
                save_already_download(dir_path[0]+download_Log[0],suolue_index)
            except Exception as e:
                print('!: E: {}'.format(e))
            break
        elif (res == '<urlopen error timed out>'):  # 超时
            color_print('!: 连接超时已跳过该图集',FOREGROUND_RED)
            break
        else:
            imghtml = lxml.etree.HTML(res)
            src_data = imghtml.xpath('//*[@class="ImageBody"]/p/a/img/@src')  # 大图页的图片地址
            src_name = imghtml.xpath('//*[@class="ImageBody"]/p/a/img/@alt')  # 图片名字

            if (len(src_data) != 1):  # 失败图片
                if (fail_times < 5):  # 如果尝试次数小于5次
                    color_print('!: 图片 {} 下载失败 (未获取到地址),尝试第 {} 次'.format(img_num, fail_times + 1),FOREGROUND_YELLOW)
                    fail_times = fail_times + 1
                    continue
                else:
                    img_fail_num = img_fail_num + 1
                    color_print('!: 图片 {} 下载失败 (未获取到地址)'.format(img_num),FOREGROUND_RED)
            else:
                pic_name = src_name[0] + '_' + str(img_num)  # 使用缩略图序号+页面号命名
                img_path = dir_path[img_org] + src_name[0] + '_' + pic_name + '.jpg'
                if os.path.isfile(img_path):
                    img_already_save_num = img_already_save_num + 1
                    color_print('*: 图片 {} 已经存在，已跳过'.format(pic_name),FOREGROUND_YELLOW)
                else:
                    try:  # 尝试下载
                        img_data = requests.get(src_data[0], timeout=10)  # 下载图片
                    except Exception as e:  # 下载超时
                        img_fail_num = img_fail_num + 1
                        color_print('!: 图片 {} 下载失败 (下载超时)'.format(pic_name),FOREGROUND_RED)
                    else:  # 下载成功则保存
                        with open(img_path, 'wb')as f:
                            f.write(img_data.content)
                            color_print("*: 图片 {} 保存成功".format(pic_name),FOREGROUND_GREEN)

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
        #try:
        link = '{}/{}'.format(url, i + 1)
        s = lxml.etree.HTML(requests.get(link).content)
        jpgLink = s.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
        filename = title + '_' + str(n) + '.jpg'
        file_path = dir_path[1] +  filename
        if os.path.isfile(file_path):
            color_print('*: 图片 {} 已经存在，已跳过'.format(filename),FOREGROUND_YELLOW)
        else:
            color_print('*: 图片 {}_{} 保存成功' .format(title, n),FOREGROUND_GREEN)
            with open(file_path, "wb+") as jpg:
                jpg.write(requests.get(jpgLink, headers=header(jpgLink)).content)
        n += 1
        #except Exception as e:
         #   print(e)
    print ('!: 图集【{}】保存成功'.format(title))
    save_already_download(dir_path[1]+download_Log[1], url)


def get_umei(num):  # 得到优美图库的详情页序列
    tag = 'yongzhuang'
    url = 'http://www.umei.cc'  # 需要设置首页地址
    page_index = url + '/tags/' + tag + '_' + str(num) + '.htm'
    response = url_open(page_index)  # 打开每一页图片
    html = lxml.etree.HTML(response)
    suolue_url = html.xpath('/html/body/div[2]/div[7]/ul/li/a/@href')
    return suolue_url


def get_mzi(pageNum):  # 获取妹子图主页列表
    baseUrl = 'http://www.mzitu.com/page/{}'.format(pageNum)
    selector = lxml.etree.HTML(requests.get(baseUrl).content)
    urls = []
    for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        urls.append(i)
    return urls

def get_page(source,page):
    if source == 1:
        return get_mzi(page)
    else:
        return get_umei(page)

def get_usr_define():
    password_list = ['000', '001', '010', '011', '100','101','110','111']
    img_org_text = ['[普通妹子]','[精选妹子]']
    download_speed_text = ['[龟速下载]','[急速下载]']
    download_page_text  = ['[只有一页]','[没有限制]']
    img_org_list = [0, 1]
    download_speed_list = [1, 10]
    download_page_list = [2, 40]

    print('=======================================================')
    print('=                     人工智障爬虫                    =')
    print('=======================================================')
    print('*: 输入指令码以开启对应功能',end='\n\n')
    print('*: 其功能区分如下表所示:',end='\n\n')

    color_print('| 【////\\\\\\\\】\t【0】             【1】   |\t\n'
          '| 【图 片 源】\t[普通妹子]\t[精选妹子]|\t\n'
          '| 【下载速度】\t[龟速下载]\t[急速下载]| \t\n'
          '| 【下载数量】\t[只有一页]\t[没有限制]| \t\n',FOREGROUND_BLUE)
    print ('如输入:101 则为选择精选妹子+龟速下载+没有限制')
    print('!: 请输入3位指令码: ', end='')
    input_num = input()
    try:
        usr_id = password_list.index(input_num)
    except Exception as e:
        color_print('!: 未输入正确指令码，将以默认值 000 运行!',FOREGROUND_RED)
        usr_id = 0
        time.sleep(1)
    fun_code = password_list[usr_id]
    img_org = img_org_list[int(fun_code[0])]
    download_speed = download_speed_list[int(fun_code[1])]
    download_page = download_page_list[int(fun_code[2])]
    color_print('!: 正为您开启 {}  {}  {} 功能...'.format(img_org_text[img_org],download_speed_text[int(fun_code[1])],download_page_text[int(fun_code[2])]), FOREGROUND_BLUE)
    return img_org, download_speed, download_page

def save_already_download(file_name, contents):
    fh = open(file_name, 'ab+')
    fh.write(base64.b64encode(contents.encode("utf-8")))
    fh.write('\n'.encode('utf-8'))
    fh.close()

if __name__ == '__main__':
    dir_path = ['D:/MyImgNew/umei/','D:/MyImgNew/mzi/']
    download_Log = ['umeiLog.bin','mziLog.bin']
    downloaded_List = []   #已下载列表
    all_url = []
    img_org, download_speed, download_page = get_usr_define()  # 获得用户权限
    if (not os.path.exists(dir_path[img_org])):
        os.makedirs(dir_path[img_org])
    else:
        pass
    color_print('!: 图片将保存在{},请尽情欣赏！'.format(dir_path[img_org]), FOREGROUND_RED)
    time.sleep(3)
    color_print('!: 请勿删除图片文件夹中的.bin文件,缺少此文件将引起断点续传功能的错误!', FOREGROUND_RED)
    print('!: 初始化页面资源中...')
    for i in range(0, download_page):
        print('!: 已加载 {}%   '.format(round((i+1) / download_page * 100)), end='')
        for proindex in range(0, round(i / download_page * 20)):
            print('■', end='')
        if i<download_page -1:
            print('', end='\r')
        else:
            print('',end='\n')
        all_url.extend(get_page(img_org, i))
    if all_url == []:
        color_print('!: 连接错误！请检查网络或重新启动！', FOREGROUND_RED)
        sys.exit(0)

    if os.path.isfile(dir_path[img_org] + download_Log[img_org]):
        print('')
        with open(dir_path[img_org] + download_Log[img_org], 'rb') as umeiList:
            for base64line in umeiList.readlines():
                line = str(base64.b64decode(base64line).decode('utf-8'))
                downloaded_List.append(line)
        umeiList.close()
    download_List=list(set(all_url) ^ set(downloaded_List))   #得到下载目录
    skip_mum = len(list(set(all_url).union(set(downloaded_List)))) - len(download_List)
    color_print('!: 已为您跳过已下载的{}个图集!'.format(skip_mum),FOREGROUND_RED)
    if img_org == 1:  #如果是妹子图源
        with ThreadPool(download_speed) as pool:
            pool.map(downloadMzitu, download_List)
    else:
        with ThreadPool(download_speed) as pool:
            pool.map(downloadUmei, download_List)
    color_print('恭喜！所有页面均已爬完~',FOREGROUND_GREEN)
