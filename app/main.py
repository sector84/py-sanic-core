from sanic import Sanic
from sanic.response import json

from routing.v1.projects import proj_routes
from routing.v1.auth import auth_routes
from core.engine.v1 import (
    SessionInterface,
    create_pg_driver,
    close_pg_drivers,
    Error,
    GLog
)
from core.utils.v1 import make_response


app = Sanic()
app.blueprint(proj_routes)
app.blueprint(auth_routes)
app.session_interface = None


@app.listener('before_server_start')
async def init(app: Sanic, loop):
    app.session_interface = SessionInterface(loop=loop, token_mode=True)
    await create_pg_driver()


@app.listener('after_server_stop')
async def close(app: Sanic, loop):
    await close_pg_drivers()


@app.exception(Exception)
def catch_errors(request, exception):
    GLog.error('При обработке запроса %s возникла ошибка', request.url)
    GLog.exception(exception)
    if isinstance(exception, Error):
        return json(exception.to_dict(), status=exception.status)
    return json(Error("Неизвестная ошибка").to_dict(), status=500)


@app.middleware('request')
async def before_request(request):
    await app.session_interface.open(request)


@app.middleware('response')
async def before_response(request, response):
    response = make_response(response)
    await app.session_interface.save(request, response)
    return response


if __name__ == '__main__':
    GLog.warning('Запуск приложения в debug-режиме')
    app.run(host='0.0.0.0', port=5000)
