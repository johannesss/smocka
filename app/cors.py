from .response import make_response


class CorsHandler:
    def __init__(self, request):
        self.request = request

    def is_preflight_request(self):
        is_options_req = self.request.method() == 'OPTIONS'
        method_header = 'Access-Control-Request-Method'
        has_preflight_header = self.request._headers.has(method_header)

        return is_options_req and has_preflight_header

    def is_cors_request(self):
        has_origin_header = self.request._headers.has('Origin')
        return has_origin_header and not self.is_same_host()

    def is_same_host(self):
        origin = self.request._headers.get('Origin')
        host = self.request._headers.get('Host')
        return origin == "http://{}".format(host)

    def add_response_headers(self, response):
        origin = self.request._headers.get('Origin')
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    def get_preflight_response(self):
        origin = self.request._headers.get('Origin')

        allow_headers = self.request._headers.get(
            'access-control-request-headers')

        allow_methods = self.request._headers.get(
            'access-control-request-method')

        headers = [
            ('Access-Control-Allow-Origin', origin),
            ('Access-Control-Allow-Methods', allow_methods),
            ('Access-Control-Allow-Credentials', 'true'),
            ('Access-Control-Allow-Headers', allow_headers)
        ]

        return make_response(status_code=204, headers=headers)
