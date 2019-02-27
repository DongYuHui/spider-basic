import re
import bs4
import json
import requests


# 会话
session = requests.Session()

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}

# 登录参数
login_param = {
    'name': '*',
    'password': '*',
    'ck': ''
}


def get_session():
    """
    获取当前会话
    """
    return session


def captcha(paylod):
    """
    提示用户输入验证码再进行登录
    """
    login_param['captcha_id'] = paylod['captcha_id']
    print('captcha url : ' + paylod['captcha_image_url'])
    login_param['captcha_solution'] = input('Please input captcha: ')
    return login()


def login():
    """
    登录
    """
    login_json = session.post('https://accounts.douban.com/j/mobile/login/basic', headers=headers, data=login_param, verify=False).json()
    if login_json['status'] == 'success':
        print('login success')
        return True
    else:
        if login_json['message'] == 'captcha_required':
            return captcha(login_json['payload'])
        else:
            print('login failed | ' + login_json['message'])
            return False