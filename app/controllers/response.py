from datetime import datetime
import time
import json

from ..database import get_response_repository
from ..response import make_response

repo = get_response_repository()


def get_ttl(ttl):
    return None if ttl == 0 else ttl


def response_has_expired(response):
    if response.get('expires') is None:
        return False

    now = datetime.now()
    expires = datetime.strptime(response.get(
        'expires'), '%Y-%m-%d %H:%M:%S.%f')

    return now > expires


def delay_if_requested(request):
    delay = request.query('delay')

    if delay is None:
        return

    if int(delay) <= 60:
        time.sleep(int(delay))

    return


class ResponseController:

    def store(self, request):
        data = request.json()

        response = repo.create(status_code=data.get('status_code'),
                               content_type=data.get('content_type'),
                               ttl=get_ttl(data.get('ttl')),
                               body=data.get('body'))

        return make_response(
            status_code=201,
            headers=[('content-type', 'application/json')],
            body=json.dumps(
                {'url': "/response/{}".format(response.get('uuid'))})
        )

    def show(self, request, uuid):
        response = repo.find_by_uuid(uuid)

        if response is None:
            return make_response(status_code=404)

        content_type = response.get('content_type')

        if response_has_expired(response):
            repo.delete_by_id(response.get('id'))
            return make_response(status_code=404)

        delay_if_requested(request)

        return make_response(status_code=response.get('status_code'),
                             headers=[('content-type', content_type)],
                             body=response.get('body'))
