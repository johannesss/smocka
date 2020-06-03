import mimetypes

from ..response import make_response


class StaticFilesController:
    def show(self, request, filename):
        file = "public/{}".format(filename.split('?')[0])

        try:
            with open(file) as f:
                contents = f.read()
                content_type = mimetypes.guess_type(file)

                return make_response(
                    status_code=200,
                    headers=[('content-type', content_type[0])],
                    body=contents)
        except IOError as e:
            print('Static files request failed', e)
            return make_response(status_code=500)
