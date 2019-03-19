import urllib.request
import re
from getPic import BaiduPicIndentify
from bs4 import BeautifulSoup
import random
import requests
import lxml
import time
import os

url='http://www.meizitu.com' #需要设置首页地址
page_num = 10 #所要爬取的页数

page_url=[]
for i in range(1,page_num+1):
    page_url.append(url  + '/a/list_1_%d.html'% (i))
print('运行时间较慢，请稍等...')
print('图片将保存在D://all中')

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
def url_open(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', random.choice(my_headers))
    response = urllib.request.urlopen(req).read().decode('gbk')
    return response;

for index_list in page_url:   #每一页
    response = url_open(index_list)
    html = lxml.etree.HTML(response)
    path_name=html.xpath('//*[@id="maincontent"]/div/ul/li/div/div/a/img/@alt')
    src_url = html.xpath('//*[@id="maincontent"]/div/ul/li/div/div/a/@href')
   
    for index_src in src_url:   #每一个缩略图
        print('============')
        starttime = time.time()
        res =  url_open(index_src)
        imghtml = lxml.etree.HTML(res)
        src_data = imghtml.xpath('//*[@id="picture"]/p/img/@src')  #详情页的图片地址
        src_name = imghtml.xpath('//*[@id="picture"]/p/img/@alt')  #详情页的图片名
         #如果不存在这个文件夹
        dir_name = str(path_name[src_url.index(index_src)])[3:10]
        if(not os.path.exists('d:/all/'+dir_name)): 
            os.makedirs('D:/all/'+dir_name)
        if src_data == [] and src_name == []: #如果数据为空，跳过
            pass
        else:
            for index_img in src_data:
                
                pic_name = src_name[src_data.index(index_img)]
                img_path = 'd:/all/'+dir_name+'/'+pic_name+'.jpg'
                if os.path.isfile(img_path):
                    print('{} 中的 {} 已经存在!'.format(dir_name,pic_name))
                else:
                    try:
                        img_data = requests.get(index_img)
                        face = BaiduPicIndentify(img_data.content)
                        face.detect_face()
                        print('---------------------------------------------')
                        face.faceout()
                        print('---------------------------------------------')
                        with open(img_path, 'wb')as f:
                            f.write(img_data.content)
                            print("正在保存{}中的 {}".format(dir_name, pic_name))
                            f.close()
                    except OSError:
                        continue
        endtime=time.time()
        print('该套图用时 {} S'.format(round(endtime-starttime)))
#print(response)
