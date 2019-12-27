from core.engine.v1 import (
    GLog,
    config,
    create_pg_driver,
    close_pg_drivers,
)


class AppDatabase:
    """Класс создания БД приложения."""

    def __init__(self, name):
        """."""
        self.sys_driver = None
        self.db_driver = None
        self.name = name

    async def __aenter__(self):
        """."""
        self.sys_driver = await create_pg_driver('postgres')
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """."""
        await close_pg_drivers()
        if exc_type is None:
            GLog.info('БД создана успешно')
            return

        GLog.warning('Ошибка. Откат изменений...')
        try:
            await self.sys_driver.execute(
                'DROP DATABASE IF EXISTS "$1";',
                [self.name]
            )
        except Exception as exp:
            GLog.exception(exp)

    async def exist(self) -> bool:
        """Проверка существования БД."""
        return bool(await self.sys_driver.select('''
            SELECT TRUE FROM pg_database
            WHERE datname = $1;
        ''', [self.name]))

    async def create(self):
        """Создание сущностей для инициализации базы."""
        msg = 'Создание БД %s'
        GLog.info(msg, self.name)

        if not await self.exist():
            GLog.info('Целевая БД еще не существует - создаем')
            GLog.debug([self.name, config.PG_CONF['user']])
            sql = "CREATE DATABASE \"%s\" ENCODING = 'UTF8' OWNER = \"%s\";"
            args = (self.name, config.PG_CONF['user'])
            await self.sys_driver.execute(sql % args)

        GLog.info('Подключение к целевой БД.')
        self.db_driver = await create_pg_driver(self.name)

        GLog.info('Создание структуры БД.')
        await self.db_driver.execute('''
            DROP TABLE IF EXISTS public."groups" CASCADE;
            CREATE TABLE public."groups" (
                "id" SERIAL NOT NULL,
                "id_parent" INT4 NOT NULL DEFAULT 0,
                "code" VARCHAR NOT NULL DEFAULT ''::varchar,
                "name" VARCHAR NOT NULL DEFAULT ''::varchar,
                "json_settings" JSON,
                PRIMARY KEY ("id")
            ) WITH (OIDS);
            COMMENT ON TABLE public."groups" IS 'Таблица групп проектов';
            
            DROP TABLE IF EXISTS public."projects" CASCADE;
            CREATE TABLE public."projects" (
                "id" SERIAL NOT NULL,
                "id_group" INT4 NOT NULL REFERENCES public."groups" ("id") 
                    ON DELETE CASCADE ON UPDATE CASCADE,
                "code" VARCHAR NOT NULL DEFAULT ''::varchar,
                "name" VARCHAR NOT NULL DEFAULT ''::varchar,
                "json_settings" JSON,
                PRIMARY KEY ("id")
            ) WITH (OIDS);
            COMMENT ON TABLE public."projects" IS 'Таблица проектов';

            DROP TABLE IF EXISTS public."users" CASCADE;
            CREATE TABLE public."users" (
                "id" SERIAL NOT NULL,
                "login" VARCHAR NOT NULL DEFAULT ''::varchar,
                "password" VARCHAR NOT NULL DEFAULT ''::varchar,
                "json_settings" JSON,
                PRIMARY KEY ("id")
            ) WITH (OIDS);
            COMMENT ON TABLE public."users" IS 'Таблица пользователи';
        ''')
