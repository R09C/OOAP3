import abc
import requests
from context import RequestContext
from exceptions import ChainException
from requests_to_selenium import message_test_message

class Handler(abc.ABC):
    def __init__(self, next_handler=None):
        self._next_handler = next_handler

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abc.abstractmethod
    def handle_request(self, context: RequestContext):
        if self._next_handler:
            return self._next_handler.handle_request(context)
        return context


class SetupRequestHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("SetupRequestHandler: Preparing headers...")
        return super().handle_request(context)


class ExecutionHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("ExecutionHandler: Sending HTTP request...")
        if not all([context.url, context.headers, context.payload_data]):
            raise ChainException(
                "ExecutionHandler: Missing URL, headers, or payload data"
            )

        try:
            response = requests.post(
                context.url,
                headers=context.headers,
                data=context.payload_data.encode("utf-8"),
            )
            context.response = response
            print(f"Request sent to {context.url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ChainException(f"ExecutionHandler: HTTP request error: {str(e)}")
        return super().handle_request(context)


class LoggingHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("LoggingHandler: Logging request details...")
        # Add logging to a file or external service
        print(f"URL: {context.url}, Session ID: {context.session_id}")
        return super().handle_request(context)


class AdminTokenHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("AdminTokenHandler: Проверка токена на администраторский статус...")
        try:
            cookie = context.session_id
            text = message_test_message(cookie)
 
            if text==b'//OK[[],0,7]':
                print("Токен подтвержден как администраторский.")
                context.is_admin = True
            else:
                print("Токен не является администраторским.")
                context.is_admin = False
        except requests.exceptions.RequestException as e:
            raise ChainException(f"AdminTokenHandler: Ошибка проверки токена: {str(e)}")

        return super().handle_request(context)


class UserChatHandler(Handler):
    def handle_request(self, context: RequestContext):
        if not context.is_admin:
            print("UserChatHandler: Отправка сообщения в чат для пользователя...")
            try:
                from requests_to_selenium import message

                # message()
                print("Сообщение успешно отправлено в чат.")
            except Exception as e:
                raise ChainException(
                    f"UserChatHandler: Ошибка отправки сообщения: {str(e)}"
                )
        else:
            print(
                "UserChatHandler: Токен администраторский, пропускаем отправку сообщения."
            )
        return super().handle_request(context)
