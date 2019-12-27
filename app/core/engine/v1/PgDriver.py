import asyncpg
import ujson

from core.engine.v1 import (
    config,
    PgDrvSingleton,
    Errors,
    Error,
    GLog
)


class PgDriver(Errors, metaclass=PgDrvSingleton):
    """Класс для удобной работы с PostgreSQL."""

    ERR_PREFIX = 'Ошибка работы с БД'

    def __init__(self, *, db_name: str = 'postgres'):
        self.db_name = db_name
        self._pool = None

    async def close(self):
        """Закрытие подключения."""
        if self._pool:
            await self._pool.close()

    @property
    def pool_exists(self):
        return self._pool is not None

    async def create_pool(self, database):
        """Создать пул подключений при необходимости."""
        if not self.pool_exists:
            self._pool = await asyncpg.create_pool(
                host=config.PG_CONF['host'],
                port=config.PG_CONF['port'],
                user=config.PG_CONF['user'],
                password=config.PG_CONF['pass'],
                database=database,
                command_timeout=60
            )

    def catch(self, error: Exception, text: str):
        """Перехват и обработка ошибки запроса."""
        # asyncpg.exceptions.PostgresError - имеет достаточно подробный метод
        # __str__ - так что его будет достаточно для описания ошибки
        error_str = str(error)
        query_str = text
        GLog.error(
            'Ошибка запроса:\n%s\n\tПричина: %s', query_str, error_str,
        )
        msg = 'ошибка синтаксиса или данных'
        self.error('%s (%s)' % (msg, error_str))

    async def select(
            self, text: str, args: list = None, one_row: bool = False,
            list_type: object = None, item_type: object = None
    ):
        """Хелпер для выполнения запросов выборки данных.

        :param str text:        Текст запроса с подстановками из args
        :param list args:       Список со значениями параметров
        :param bool one_row:    Указывает, что нужна только первая строка
        :param object list_type: Тип списка, в который будет идти загрузка
        :param object item_type: Тип элемента, в который будет идти загрузка
        """
        list_type = list_type or list
        item_type = item_type or dict
        if args is None:
            args = []

        try:
            async with self._pool.acquire() as con:
                await con.set_type_codec(
                    'json',
                    encoder=ujson.dumps,
                    decoder=ujson.loads,
                    schema='pg_catalog'
                )
                if one_row:
                    return item_type(self.expect(
                        await con.fetchrow(text, *args),
                        msg='',
                        status=404)
                    )
                result = list_type()
                for row in await con.fetch(text, *args):
                    result.append(item_type(row))
                return result
                # todo: добавить возможность выборки через генератор
                # https://magicstack.github.io/asyncpg/current/api/index.html#cursors
        except Error as e:
            raise e
        except asyncpg.exceptions.PostgresError as error:
            self.catch(error, text)
        except Exception as error:
            self.catch(error, text)

    async def execute(self, text: str, args: list = None,
                      many: bool=False, with_result: bool=False):
        """Хелпер для выполнения всех запросов, кроме select.

        :param text:        Текст запроса с подстановками из args
        :param args:        Список со значениями параметров
        :param many:        Флаг, определяющий множественную вставку
        :param with_result: Флаг, возвращать ли результат выполнения запроса
        """
        if args is None:
            args = []
        async with self._pool.acquire() as con:
            try:
                await con.set_type_codec(
                    'json',
                    encoder=ujson.dumps,
                    decoder=ujson.loads,
                    schema='pg_catalog'
                )
                # Выполняем запрос
                if many:
                    await con.executemany(text, args)
                else:
                    if with_result:
                        return await con.fetchval(text, *args)
                    else:
                        await con.execute(text, *args)
                # например если в запросе есть RETURNING id или что-то такое
            except asyncpg.exceptions.PostgresError as error:
                self.catch(error, text)
            except Exception as error:
                self.catch(error, text)


async def create_pg_driver(database: str=None) -> PgDriver:
    """Создать экземпляр класса драйвера работы с ПГ.

    :return: Экземпляр класса PgDriver
    """
    database = database or config.PG_CONF['dbname']
    result = PgDriver(db_name=database)
    await result.create_pool(database)
    return result


async def close_pg_drivers():
    """Закрыть все подключения к ПГ."""
    for instance in PgDriver._instances.values():
        await instance.close()
    PgDriver._instances.clear()
