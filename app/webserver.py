import errno
import os
import signal
import socket

from .events import Events
from .request import Request
from .response import make_response


class Webserver:
    def __init__(self, server_address):
        self.address_family = socket.AF_INET
        self.socket_type = socket.SOCK_STREAM
        self.request_queue_size = 1024
        self.request_max_size = 10240
        self.respond_to_http_verbs = (
            'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS')

        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )

        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(server_address)
        listen_socket.listen(self.request_queue_size)

        host, port = self.listen_socket.getsockname()[:2]

        self.server_name = socket.getfqdn(host)
        self.host = host
        self.server_port = port

        self.events = Events()

    def serve_forever(self):
        print("Serving HTTP on port http://{}:{} ..".format(
            self.host, self.server_port))

        signal.signal(signal.SIGCHLD, self._grim_reaper)

        while True:
            try:
                client_connection, client_address = self.listen_socket.accept()
            except IOError as e:
                code, msg = e.args
                # restart 'accept' if it was interrupted
                if code == errno.EINTR:
                    continue
                else:
                    raise

            pid = os.fork()
            if pid == 0:  # child
                self.listen_socket.close()  # close child copy
                self._handle_request(client_connection, client_address)
                client_connection.close()
                os._exit(0)
            else:  # parent
                client_connection.close()  # close parent copy and loop over

    def _grim_reaper(self, signum, frame):
        while True:
            try:
                pid, status = os.waitpid(
                    -1,          # Wait for any child process
                    os.WNOHANG   # Do not block and return EWOULDBLOCK error
                )
            except OSError:
                return

            if pid == 0:  # no more zombies
                return

    def _handle_request(self, client_connection, client_address):
        request_data = client_connection.recv(self.request_max_size)

        if not request_data:
            return

        self.request = Request(request_data.decode(), client_address)

        # self.request.print()

        if self.request.method() in self.respond_to_http_verbs:
            self.events.dispatch('request', self.request, client_connection)
        else:
            print("HTTP verb {} not in respond_to_http_verbs, ignoring."
                  .format(self.request.method()))

            client_connection.sendall(
                make_response(405)
            )
