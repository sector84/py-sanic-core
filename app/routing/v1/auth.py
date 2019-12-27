from sanic.response import json
from sanic import Blueprint
from entities.v1 import User
from core.engine.v1 import SessionInterface


auth_routes = Blueprint('auth_routes')


@auth_routes.post('/api/1.0/auth/login/')
async def login(request):
    user = await User.get_by_credentials(
        request.form.get('login'),
        request.form.get('password')
    )
    SessionInterface.new_sid(request)
    request['session']['id'] = user.id
    request['session']['login'] = user.login
    return json({"token": request['session'].sid})


@auth_routes.get('/api/1.0/auth/authorized/')
async def authorized(request):
    return json({
        'res': bool(request['session'].get('id') and request['session'].get('login'))
    })


@auth_routes.post('/api/1.0/auth/logout/')
async def logout(request):
    request['session'].clear()
    return json({})
