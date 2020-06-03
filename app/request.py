import json

from .header_bag import HeaderBag


class Request:
    def __init__(self, text, client_address):
        lines = text.splitlines()

        self.client_address = client_address

        (self._method,
         self._path,
         self._version) = self._parse_start_line(lines[0])

        self._headers = self._parse_headers(lines[1:])

        self._body = self._parse_body(
            lines[self._headers.count() + 2:]
        )

    def query(self, get_param=None):
        pieces = self.path().split('?')

        if len(pieces) <= 1:
            return None

        params = {}
        for piece in pieces[1].split('&'):
            (param, value) = piece.split('=')
            params[param] = value

        if get_param is not None:
            return params.get(get_param)

        return params

    def version(self):
        return self._version

    def path(self):
        return self._path

    def method(self):
        return self._method.upper()

    def headers(self):
        return self._headers.get_all()

    def body(self):
        return self._body

    def is_json(self):
        content_type = self._headers.get('content-type')
        return content_type == 'application/json'

    def wants_json(self):
        accept = self._headers.get('accept')
        return accept == 'application/json'

    def json(self):
        if self.is_json():
            return json.loads(self._body)

    def print(self):
        headers = ''
        for (header, value) in self._headers.get_all():
            headers += "- {}: {}\r\n".format(header, value)

        print("""
--------------------------------
Retrieved request.

IP address: {}
Method: {}
Path: {}
Version: {}
Headers:
{}
Body: {}
--------------------------------""".format(
            self.client_address[0],
            self.method(),
            self.path(),
            self.version(),
            headers,
            self.body()))

    def _parse_start_line(self, line):
        return line.rstrip('\r\n').split()

    def _parse_headers(self, lines):
        headers = HeaderBag()

        i = 0
        while i < len(lines) and lines[i] != '':
            (header, value) = lines[i].split(': ')
            headers.add(header, value)
            i += 1

        return headers

    def _parse_body(self, lines):
        if len(lines) == 0:
            return ''

        if self._headers.has('content-length'):
            body = ''
            body = body.join(lines)
            content_length = int(self._headers.get('content-length'))
            return body[0:content_length]
