from sanic import Blueprint
from core.utils.v1 import login_required
from core.engine.v1 import (
    GLog,
)

from entities.v1 import (
    Projects,
    Project
)


proj_routes = Blueprint('proj_routes')
proj_routes.static('/static', './static')


@proj_routes.get('/api/1.0/projects/<id_group:int>/')
async def projects(request, id_group: int):
    GLog.debug(request)
    return await Projects.list(id_group)


@proj_routes.post('/api/1.0/projects/<id_group:int>/')
@login_required
async def project_create(request, id_group: int):
    GLog.debug(request)
    GLog.debug(request.json)
    return await Project.create(id_group, request.json)


@proj_routes.get('/api/1.0/groups/')
@login_required
async def groups(request):
    # todo: реализация
    # Урла для проверка закрытых от паблика api
    from sanic.response import json
    GLog.debug(request)
    return json({'1': 2})
