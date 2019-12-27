import ujson
from core.engine.v1 import (
    Checks,
    PgDriver,
    create_pg_driver
)


class BaseItem(dict, Checks):
    """Базовый класс для сущностей.

    :param list[tuple]|dict data: Значения для инициализации
    """
    MAPPING_JSON = {}
    _pg = None

    async def pg(self) -> PgDriver:
        """Получение объекта подключения к БД."""
        if self._pg is None:
            self._pg = await create_pg_driver()
        return self._pg

    def load_from_json(self, data):
        """Загрузка полей сущности из данных (json|dict)."""
        if not isinstance(data, dict):
            try:
                data = ujson.loads(data)
            except Exception as e:
                err = 'Ошибка загрузки данных из JSON: %s' % str(e)
                self.error(err)

        for self_name, data_name in self.MAPPING_JSON.items():
            if data_name not in data:
                continue

            _item = self
            _item.__setattr__(self_name, data[data_name])
        return self
