from http import HTTPStatus

from .header_bag import HeaderBag


def make_response(status_code=200, headers=[], body=''):
    return Response(status_code, headers, body)


class Response:
    def __init__(self, status_code, headers=[], body='', encoding='UTF-8'):
        self.status_code = status_code
        self.headers = HeaderBag(headers)
        self.body = body
        self.encoding = encoding

        if self.body:
            content_length = len(self.body.encode(self.encoding))
            self.headers.add('content-length', content_length)

    def to_utf8(self):
        return self.to_string().encode('UTF-8')

    def to_string(self):
        CRLF = '\r\n'

        status = self.get_status()
        start_line = """\
HTTP/1.1 {} {}""".format(status.value, status.phrase)

        if self.headers.count() == 0:
            return (start_line +
                    CRLF +
                    CRLF +
                    self.body)

        headers = ''
        for (header, value) in self.headers.get_all():
            headers += "{}: {}\r\n".format(header, value)

        if self.headers.count() > 0:
            return (start_line +
                    CRLF +
                    headers +
                    CRLF +
                    self.body)

    def get_status(self):
        return HTTPStatus(self.status_code)

    def print(self):
        headers = ''
        for (header, value) in self.headers.get_all():
            headers += "- {}: {}\r\n".format(header, value)

        print("""
--------------------------------
Returning response:

Status code: {}
Headers:
{}
Body:
{}
--------------------------------""".format(
            self.status_code,
            headers,
            self.body))
