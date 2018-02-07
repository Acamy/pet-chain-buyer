# -*- coding:utf-8 -*-
import requests
import time
import threadpool
import json
import configparser
import traceback
import base64
from PIL import Image
from urllib import request, parse
import ocr

class PetChain():
    def __init__(self):
        self.degree_map = {
            0: "common",
            1: "rare",
            2: "excellence",
            3: "epic",
            4: "mythical",
        }
        self.isAuto=False
        self.degree_conf = {}
        self.interval = 1
        self.seed = ''
        self.cookies = ''
        self.username = ''
        self.password = ''
        self.captcha = ''
        self.headers = {}
        self.get_headers()
        self.get_config()

    def get_config(self):
        config = configparser.ConfigParser()
        config.read("config/config.ini")
        self.mode = config.getint("Pet-Chain", "mode")
        self.isThreadPool = config.getboolean("Pet-Chain", "isThreadPool")
        for i in range(5):
            try:
                amount = config.getfloat("Pet-Chain", self.degree_map.get(i))
            except Exception as e:
                amount = 100
            self.degree_conf[i] = amount
        self.showapi_appid = config.get("ShowAPI", "appid")
        self.showapi_sign = config.get("ShowAPI", "sign")

    def get_headers(self):
        with open("config/headers.txt") as f:
            lines = f.readlines()
            for line in lines:
                splited = line.strip().split(":")
                key = splited[0].strip()
                value = ":".join(splited[1:]).strip()
                self.headers[key] = value

    def get_market(self):
        try:
            data = {
                "appId":1,
                "lastAmount":1,
                "lastRareDegree":0,
                "pageNo":1,
                "pageSize":20,
                "petIds":[],
                "querySortType": "AMOUNT_ASC",
                "requestId": int(round(time.time() * 1000)),
                "tpl": "",
            }
            page = requests.post("https://pet-chain.baidu.com/data/market/queryPetsOnSale", headers=self.headers, data=json.dumps(data))
            errorMsg = page.json().get(u"errorMsg")

            if errorMsg == u"success":
                pets = page.json().get(u"data").get("petsOnSale")

                if self.isThreadPool:
                    pool = threadpool.ThreadPool(10)
                    req = threadpool.makeRequests(self.purchase, pets)
                    for queue in req:
                        pool.putRequest(queue)
                    pool.wait()
                else:
                    pet0 = pets[0]
                    self.purchase(pet0)

        except Exception as e:
            print('Exception in get_market!')

    def purchase(self, pet):
        try:
            pet_amount = pet.get(u"amount")
            pet_degree = pet.get(u"rareDegree")
            setting = self.degree_conf.get(pet_degree)
            category = self.degree_map.get(pet_degree)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ', 当前最低价格: ' + pet_amount + ", 种类为: " + category + ", petId为:" + pet.get(u"petId"))
            if float(pet_amount) <= setting:
                imgstr = self.getCaptchaStr()
                if imgstr != "error":
                    print("============================正在尝试购买============================")
                    if self.mode == 1:
                        self.genCaptchaImg(imgstr)
                        img = Image.open("./captcha.jpg")
                        self.captcha = ocr.ocr_img(img)
                    elif self.mode == 2:
                        self.captcha = self.getCaptchaByApi(imgstr)
                    else:
                        self.genCaptchaImg(imgstr)
                        self.captcha = input('请输入验证码：')

                    pet_id = pet.get(u"petId")
                    pet_validcode = pet.get(u"validCode")
                    data = {"petId": pet_id,
                            "amount": "{}".format(pet_amount),
                            "seed": self.seed,
                            "captcha": self.captcha,
                            "validCode": pet_validcode,
                            "requestId": int(round(time.time() * 1000)),
                            "appId": 1,
                            "tpl": ""
                            }
                    page = requests.post("https://pet-chain.baidu.com/data/txn/create", headers=self.headers, data=json.dumps(data), timeout=2)

                    print(json.dumps(page.json(), ensure_ascii=False))
        except Exception as e:
            traceback.print_exc()

    def getCaptchaStr(self):
        data = {
            "appId": 1,
            "requestId": int(round(time.time() * 1000)),
            "tpl": "",
        }
        page = requests.post("https://pet-chain.baidu.com/data/captcha/gen", headers=self.headers, data=json.dumps(data), timeout=2)

        jPage = page.json()

        if jPage.get(u"errorMsg") == "success":
            self.seed = jPage.get(u"data").get(u"seed")
            return jPage.get(u"data").get(u"img")
        else:
            print('获取验证码失败！')
            return "error"

    def genCaptchaImg(self, imgStr):
        if imgStr != "error":
            with open('captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(imgStr))

    def getCaptchaByApi(self, img):
        self.get_config()
        url = "http://route.showapi.com/184-5"
        send_data = parse.urlencode([
            ('showapi_appid', self.showapi_appid)
            , ('showapi_sign', self.showapi_sign)
            , ('img_base64', img)
            , ('typeId', "34")
            , ('convert_to_jpg', "0")

        ])

        req = request.Request(url)
        try:
            response = request.urlopen(req, data=send_data.encode('utf-8'), timeout=10)  # 10秒超时反馈
        except Exception as e:
            print(e)
        result = response.read().decode('utf-8')
        result_json = json.loads(result)
        print('result_json data is:', result_json)
        return result_json.get(u"showapi_res_body").get(u"Result")

if __name__ == "__main__":
    pc = PetChain()
    #pc.getCaptchaStr()
    while True:
        pc.get_market()
        time.sleep(2) # 每隔三秒执行一次