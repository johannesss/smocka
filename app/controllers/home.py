from app.response import make_response


class HomeController:
    def index(self, request):
        hello_world = 'public/index.html'

        try:
            with open(hello_world) as file:
                contents = file.read()

                return make_response(
                    status_code=200,
                    headers=[('content-type', 'text/html')],
                    body=contents)
        except IOError:
            return make_response(status_code=500)
