import json
from http import HTTPStatus

from ..response import make_response


class SettingsController:
    def get(self, request):
        status_codes = []
        for status in list(HTTPStatus):
            status_codes.append({
                'value': status.value,
                'text': "{} ({})".format(status.value, status.phrase)
            })

        content_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'text/html',
            'text/xml',
            'text/css',
            'text/plain',
            'text/csv',
            'multipart/form-data'
        ]

        content_types.sort()

        response = {
            'status_codes': status_codes,
            'content_types': content_types
        }

        return make_response(
            status_code=200,
            headers=[('content-type', 'application/json')],
            body=json.dumps(response)
        )
