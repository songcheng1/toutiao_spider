# -*- coding: utf-8 -*-
import urllib
import urllib.parse
import requests


def get_json():
    url = "https://www.toutiao.com/api/pc/feed/"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "referer": "https://www.toutiao.com/ch/news_tech/",
    }
    params = {
        "category": "news_tech",
        "utm_source": "toutiao",
        "widen": "1",
        "max_behot_time": "0",
        "max_behot_time_tmp": "0",
        "tadrequire": "true",
        "as": "",
        "cp": "",
    }

    group_data = requests.get('http://localhost:5602/business-demo/invoke?group=ws-group&action=clientTime')

    _signature = group_data.json().get('data')

    print("计算_signature值为：", _signature)
    params["_signature"] = _signature
    resp = requests.get(url, headers=headers, params=params)
    print(resp.json())


if __name__ == '__main__':
    get_json()
