from config import XSS_PAYLOAD_TEMPLATE, CALLBACK_URL


class RequestContext:
    def __init__(self, url, base_headers, session_id):
        self.url = url
        self.headers = base_headers.copy()
        self.xss_payload_template = XSS_PAYLOAD_TEMPLATE
        self.session_id = session_id
        self.payload_data = None
        self.response = None
        self.error = None
        self.callback_url = CALLBACK_URL

    def get_formatted_xss_payload(self):
        return self.xss_payload_template.format(callback_url=self.callback_url)
