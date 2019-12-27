import uuid
import ujson
import aiomcache
from sanic_session.base import SessionDict
from sanic_session import MemcacheSessionInterface

from core.engine.v1 import (
    config,
)


class SessionInterface(MemcacheSessionInterface):
    def __init__(self, **kwargs):
        mc_client = aiomcache.Client(config.MC_CONF['host'],
                                     port=config.MC_CONF['port'],
                                     loop=kwargs.pop('loop', None))
        self._token_mode = kwargs.pop('token_mode', True)
        super().__init__(mc_client, **kwargs)

    def get_sid(self, request) -> str:
        """Получить идентификатор сессии."""
        if self._token_mode:
            return request.raw_args.get('token', request.form.get('token', ''))
        else:
            return request.cookies.get(self.cookie_name, '')

    async def open(self, request) -> dict:
        """Opens a session onto the request. Restores the client's session
        from memcache if one exists.The session data will be available on
        `request.session`.


        Args:
            request (sanic.request.Request):
                The request, which a session will be opened onto.

        Returns:
            dict:
                the client's session data,
                attached as well to `request.session`.
        """
        # sid = request.cookies.get(self.cookie_name)
        sid = self.get_sid(request)

        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            key = (self.prefix + sid).encode()
            val = await self.memcache_connection.get(key)

            if val is not None:
                data = ujson.loads(val.decode())
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        # attach the session data to the request, return it for convenience
        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session to memcache.

        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.Response):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.

        Returns:
            None
        """
        if 'session' not in request:
            return

        key = (self.prefix + request['session'].sid).encode()

        if not request['session']:
            await self.memcache_connection.delete(key)

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = ujson.dumps(dict(request['session'])).encode()

        await self.memcache_connection.set(
            key, val,
            exptime=self.expiry)

        if not self._token_mode:
            self._set_cookie_expiration(request, response)
        else:
            self._delete_cookie(request, response)

    @classmethod
    def new_sid(cls, request):
        """Сгенерировать новый индентификатор сессии."""
        if 'session' in request:
            request['session'].sid = uuid.uuid4().hex
