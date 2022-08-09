# -*-coding:utf-8-*-
__author__ = 'Sunny'

import requests
from bs4 import BeautifulSoup
import time

url = '***'



def send_notice(text):
    line_url = "***"
    params = {"message": "{}".format(text)}
    r = requests.post(line_url, headers=headers, params=params)
    # print(r.status_code)  # 200

    params = {"message": "{}".format(text)}
    r2 = requests.post(line_url, headers=headers2, params=params)



bagtime = 0
while 1:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        now = int(time.time())
        
        if now - bagtime > 3600:
            for link in soup.find_all('a'):
                target = str(link.get('href'))
                if '/product' in target and 'py' in target:
                    color = str(link).split('</span>')[1].split(' ')[2]
                    color = ' --' + color
                    bagtime = now
                    name = target.split('product/')[1].split('-H')[0]
                    bag = '\n' + name + color + '\n' + '***' + target
                    print(bag)
                    send_notice('{}'.format(bag))

        print('Run')
        time.sleep(10)
    except Exception as e:
        print(e)
        time.sleep(10)
