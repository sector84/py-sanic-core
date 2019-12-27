from functools import wraps

from sanic.response import json, HTTPResponse
from core.base.v1 import (
    BaseItem,
    BaseList,
)
from core.engine.v1 import Errors


def make_response(response):
    """Сформировать sanic.HTTPResponse из того, что вернуло наше приложение.

    :param response: объект возврата на оработку урлов
    :return: sanic.HTTPResponse
    """

    if isinstance(response, BaseItem) or isinstance(response, BaseList):
        if hasattr(response, 'to_http'):
            response = json(response.to_http())
        else:
            response = json(response)

    # todo: расширить поддержку объектов ответа (базовые типы?)
    msg = 'Неизвестный тип ответа'
    Errors.expect(isinstance(response, HTTPResponse), msg=msg)
    return response


def login_required(f):
    @wraps(f)
    def login_required_wrapper(request, *args, **kwargs):
        if 'session' not in request:
            Errors.error('', status=401)
        if not request['session'].get('id') or not request['session'].get('login'):
            Errors.error('', status=401)
        return f(request, *args, **kwargs)

    return login_required_wrapper

