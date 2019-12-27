from hashlib import sha256

from core.base.v1 import (
    BaseItem,
)
from core.engine.v1 import (
    GLog,
    Error,
    create_pg_driver,
)


class User(BaseItem):
    """Пользователь.

    :param list|dict data:  Данные для инициализации
    """

    ERR_PREFIX = 'Ошибка работы с пользователем'

    def toDict(self) -> dict:
        """Правильное представление для сериализации в JSON через ujson."""
        return {
            'id': self['id'],
            'login': self['login'],
            'json_settings': self['json_settings'],
        }

    @property
    def id(self):
        return self['id']

    @property
    def login(self):
        return self['login']

    @property
    def json_settings(self):
        return self['json_settings']

    @classmethod
    async def get_by_credentials(cls, login: str, passw: str) -> BaseItem:
        """Выбрать пользователя по логину и паролю.

        :param login:    Логин пользователя
        :param passw:    Пароль пользователя
        :rtype entities.v1.User
        """
        GLog.info('Выборка пользователя')
        login = cls.check_str(login, arg='Логин пользователя')
        passw = cls.check_str(passw, arg='Пароль пользователя')
        passw = sha256(passw.encode('utf-8')).hexdigest()

        pg = await create_pg_driver()
        sql = '''
          SELECT * FROM public."users" 
          WHERE "login" = $1 AND "password" = $2;
        '''
        args = [login, passw]
        try:
            return await pg.select(sql, args, item_type=cls, one_row=True)
        except Error as err:
            if err.status == 404:
                # пользователь не найден - значит ошибка авторизации
                cls.error('Пользователь не найден', status=401)
