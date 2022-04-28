"""
@File:Dingtalk.py
@author:yangwuxie
@date: 2021/01/20
"""

import requests
import json


def send_ding(content: str, DingtalkAccessToken: str):
    try:
        url = DingtalkAccessToken
        pagrem = {
            "msgtype": "text",
            "text": {
                "content": "platform:" + content
            },
            "isAtAll": True
        }
        headers = {
            'Content-Type': 'application/json'
        }
        f = requests.post(url, data=json.dumps(pagrem), headers=headers)
        if f.status_code == 200:
            return True
        else:
            return False
    except:
        return False
