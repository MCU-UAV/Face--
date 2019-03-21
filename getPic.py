import base64
import json
import requests


class BaiduPicIndentify:
    def __init__(self, img):
        self.AK = "aotCVGwzQrGUhjbBLUgHAfnw"
        self.SK = "waDjfTeo0yNNIkP1vlW8q0RMkWgSyaO6"
        self.img_src = img
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.face_num = 0
        self.age = -1  # double
        self.beauty = -1  # int64 0-100
        self.race = 'none'  # yellow: 黄种人 white: 白种人 black:黑种人 arabs: 阿拉伯人
        self.gender = 'none'  # male:男性 female:女性
        self.expression = 'none'  # none:不笑；smile:微笑；laugh:大笑
        self.face_shape = 0
        self.emotion = 'none'
        self.glasses = 'none'
        self.dicRace = {'yellow': '黄种人', 'white': '白种人', 'black': '黑种人', 'arabs': '阿拉伯人'}
        self.dicGender = {'male': '男性', 'female': '女性'}
        self.dicExpression = {'none': '不笑', 'smile': '微笑', 'laugh': '大笑'}
        self.dicFace_shap = {'square': '正方形', 'triangle': '三角形', 'oval': '椭圆', 'heart': '心形', 'round': '圆形'}
        self.dicEmotion = {'angry': '愤怒', 'disgust': '厌恶', 'fear': '恐惧', 'happy': '高兴', 'sad': '伤心', 'surprise': '惊讶',
                           'neutral': '无情绪'}
        self.dicGlasses = {'none': '无眼镜', 'common': '普通眼镜', 'sun': '墨镜'}

    def faceout(self):
        if (self.face_num == 0):
            print('未识别到人脸！')
        else:
            print('[人数]: {} [年龄]: {} [颜值]: {} [脸型]: {} \n'
                  '[人种]: {} [性别]: {} [表情]: {} [情绪]: {} [眼镜]:{}'.format(self.face_num,
                                                             self.age, self.beauty,
                                                             self.dicFace_shap[self.face_shape],
                                                             self.dicRace[self.race],
                                                             self.dicGender[self.gender],
                                                             self.dicExpression[self.expression],
                                                             self.dicEmotion[self.emotion],
                                                             self.dicGlasses[self.glasses]));

    def get_accessToken(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + self.AK + '&client_secret=' + self.SK
        response = requests.get(host, headers=self.headers)
        json_result = json.loads(response.text)
        return json_result['access_token']

    def img_to_BASE64(self):
        base64_data = base64.b64encode(self.img_src)
        return base64_data

    def detect_face(self):
        # 人脸检测与属性分析
        # img_BASE64 = self.img_to_BASE64()
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        post_data = {
            "image": self.img_src,
            "image_type": "URL",
            "face_field": "gender,age,beauty,race,expression,face_shape,glasses,emotion",
            "face_type": "LIVE"
        }
        access_token = self.get_accessToken()
        request_url = request_url + "?access_token=" + access_token
        response = requests.post(url=request_url, data=post_data, headers=self.headers)
        json_result = json.loads(response.text)
        if json_result['error_msg'] != 'SUCCESS':
            print(json_result['error_msg'])
        if json_result['error_msg'] != 'pic not has face' and json_result['error_msg'] == 'SUCCESS':
            # print("图片中包含人脸数：", json_result['result']['face_num'])
            # print("图片中包含人物年龄：", json_result['result']['face_list'][0]['age'])
            # print("图片中包含人物颜值评分：", json_result['result']['face_list'][0]['beauty'])
            # print("图片中包含人物性别：", json_result['result']['face_list'][0]['gender']['type'])
            # print("图片中包含人物种族：", json_result['result']['face_list'][0]['race']['type'])
            ##print("图片中包含人物表情：", json_result['result']['face_list'][0]['expression']['type'])
            self.face_num = json_result['result']['face_num']
            self.age = json_result['result']['face_list'][0]['age'];
            self.beauty = json_result['result']['face_list'][0]['beauty'];
            self.gender = json_result['result']['face_list'][0]['gender']['type'];
            self.race = json_result['result']['face_list'][0]['race']['type'];
            self.expression = json_result['result']['face_list'][0]['expression']['type']
            self.face_shape = json_result['result']['face_list'][0]['face_shape']['type']
            self.emotion = json_result['result']['face_list'][0]['emotion']['type']
            self.glasses = json_result['result']['face_list'][0]['glasses']['type']


def getPic(url):
    # img_src = input('请输入需要检测的本地图片路径:')
    # img_src="https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=1240817690,4214518707&fm=26&gp=0.jpg"     #test url

    baiduDetect = BaiduPicIndentify(url)
    baiduDetect.detect_face()
    return baiduDetect;
