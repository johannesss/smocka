from .cors import CorsHandler
from .response import make_response
from .router import MethodNotAllowedException, PathNotFoundException, Router
from .webserver import Webserver


def make_application(host='', port=80):
    router = Router()
    webserver = Webserver((host, port))

    app = Application(router, webserver)

    return [app, app.router, app.webserver]


class Application:
    def __init__(self, router, webserver):
        self.router = router
        self.webserver = webserver

    def start(self):
        self._setup_event_listeners()
        self.webserver.serve_forever()

    def _setup_event_listeners(self):
        self.webserver.events.listen('request', self._handle_request)

    def _handle_request(self, request, conn):

        cors_handler = CorsHandler(request)

        if cors_handler.is_preflight_request():
            response = cors_handler.get_preflight_response()

            return conn.sendall(response.to_utf8())

        try:
            response = self.router._match(request)

            if cors_handler.is_cors_request():
                response = cors_handler.add_response_headers(response)

            return conn.sendall(response.to_utf8())
        except PathNotFoundException:
            return conn.sendall(make_response(404).to_utf8())
        except MethodNotAllowedException:
            return conn.sendall(make_response(405).to_utf8())

        return conn.sendall(response.to_utf8())
