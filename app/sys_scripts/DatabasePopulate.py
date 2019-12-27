from hashlib import sha256

from core.engine.v1 import (
    GLog,
    create_pg_driver,
    close_pg_drivers,
)


class AppDatabasePopulate:
    """Класс наполнения БД приложения данными тестовыми данными."""

    def __init__(self, name):
        """."""
        self.db_driver = None
        self.name = name

    async def __aenter__(self):
        """."""
        self.db_driver = await create_pg_driver(self.name)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """."""
        await close_pg_drivers()
        if exc_type is None:
            GLog.info('БД наполнена успешно')
            return

        GLog.warning('Ошибка. Откат изменений...')
        try:
            await self.db_driver.execute(
                'TRUNCATE "projects", "groups", "users" RESTART IDENTITY;',
                []
            )
        except Exception as exp:
            GLog.exception(exp)

    async def populate(self):
        """Наполнение БД."""
        msg = 'Наполнение БД %s'
        GLog.info(msg, self.name)

        GLog.info('Очистка существующих данных')
        await self.db_driver.execute(
            'TRUNCATE "projects", "groups", "users" RESTART IDENTITY;',
            []
        )

        GLog.info('Наполнение таблицы "groups"')
        await self.db_driver.execute('''
            INSERT INTO public."groups" (
                "id_parent", "code", "name", "json_settings"
            ) VALUES ($1, $2, $3, $4::json);
        ''', [
            (0, 'root_gr', 'Корневая', {"balance": 7.77, "active": True}),
            (1, 'sub_gr1', 'Подгруппа', {"balance": 88.99, "active": False})
        ], many=True)

        GLog.info('Наполнение таблицы "projects"')
        await self.db_driver.execute('''
            INSERT INTO public."projects" (
                "id_group", "code", "name", "json_settings"
            ) VALUES ($1, $2, $3, $4);
        ''', [
            (1, 'prj1', 'Проект 1', {"active": True}),
            (2, 'prj2', 'Проект 2', {"active": False})
        ], many=True)

        GLog.info('Наполнение таблицы "users"')
        await self.db_driver.execute('''
            INSERT INTO public."users" (
                "login", "password", "json_settings"
            ) VALUES ($1, $2, $3);
        ''', [
            ('user1', sha256('123'.encode('utf-8')).hexdigest(), None),
            ('user2', sha256('321'.encode('utf-8')).hexdigest(), None)
        ], many=True)
        GLog.info('созданы 2 пользователя: (user1: 123), (user2: 321)')
