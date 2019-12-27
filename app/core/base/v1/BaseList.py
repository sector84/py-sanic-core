from collections import deque

from core.engine.v1 import (
    Checks,
    PgDriver,
    create_pg_driver
)


class BaseList(deque, Checks):
    """Базовый класс для списка сущностей.

    :param list data: Значения для инициализации
    """

    _pg = None

    async def pg(self) -> PgDriver:
        """Получение объекта подключения к БД."""
        if self._pg is None:
            self._pg = await create_pg_driver()
        return self._pg

    # todo: при необходимости добавить метод load_from_json(self, data):
