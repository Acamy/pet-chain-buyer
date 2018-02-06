# -*- coding:utf-8 -*-
import requests
import time
import threadpool
import json
import configparser
import traceback
import base64
from PIL import Image
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
        self.isAuto = config.getboolean("Pet-Chain", "isAuto")
        for i in range(5):
            try:
                amount = config.getfloat("Pet-Chain", self.degree_map.get(i))
            except Exception as e:
                amount = 100
            self.degree_conf[i] = amount

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
            print(errorMsg + '================================================')
            if errorMsg == u"success":
                pets = page.json().get(u"data").get("petsOnSale")
                pool = threadpool.ThreadPool(10)
                req = threadpool.makeRequests(self.purchase, pets)
                for queue in req:
                    pool.putRequest(queue)
                pool.wait()
        except Exception as e:
            print(e)

    def purchase(self, pet):
        try:
            pet_amount = pet.get(u"amount")
            pet_degree = pet.get(u"rareDegree")
            setting = self.degree_conf.get(pet_degree)

            if float(pet_amount) <= setting:
                if self.genCaptcha(): # 生成验证码
                    img = Image.open("./captcha.jpg")
                    if self.isAuto:
                        self.captcha = ocr.ocr_img(img)
                    else:
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
                    category = self.degree_map.get(pet_degree)
                    page = requests.post("https://pet-chain.baidu.com/data/txn/create", headers=self.headers, data=json.dumps(data), timeout=2)
                    print(category + ':' + pet_amount + "; " + json.dumps(page.json(), ensure_ascii=False))
        except Exception as e:
            traceback.print_exc()

    def genCaptcha(self):
        data = {
            "appId": 1,
            "requestId": int(round(time.time() * 1000)),
            "tpl": "",
        }
        page = requests.post("https://pet-chain.baidu.com/data/captcha/gen", headers=self.headers, data=json.dumps(data), timeout=2)
        jPage = page.json()
        if jPage.get(u"errorMsg") == "success":
            self.seed = jPage.get(u"data").get(u"seed")
            img = jPage.get(u"data").get(u"img")
            with open('captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(img))
            return True
        else:
            print('获取验证码失败！')
            return False


if __name__ == "__main__":
    pc = PetChain()
    #pc.genCaptcha()
    while True:
        pc.get_market()
        time.sleep(3) # 每隔三秒执行一次