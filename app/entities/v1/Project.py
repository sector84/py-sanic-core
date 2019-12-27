from core.base.v1 import (
    BaseList,
    BaseItem,
)
from core.engine.v1 import (
    GLog,
    create_pg_driver,
)


class Project(BaseItem):
    """Проект.

    :param list|dict data:  Данные для инициализации
    """

    MAPPING_JSON = {
        # self_name -> json_name
        'ID':            "id",
        'id_group':      "id_group",
        'code':          "code",
        'name':          "name",
        'json_settings': "json_settings",
    }
    ERR_PREFIX = 'Ошибка работы с проектом'

    def toDict(self) -> dict:
        """Правильное представление для сериализации в JSON через ujson."""
        return {
            'id': self.ID,
            'id_group': self.id_group,
            'code': self.code,
            'name': self.name,
            'json_settings': self.json_settings,
        }

    def _check(self):
        """Проверка данных"""
        if 'id' in self:
            self.ID = self['id']
        self.id_group = self['id_group']
        self.code = self['code']
        self.name = self['name']
        self.json_settings = self['json_settings']

    async def _create(self):
        """."""
        GLog.debug('Вставка проекта в БД')

        # todo: корявенько - перепродумать для более ровной реализации
        pg = await self.pg()
        self.ID = await pg.execute('''
            INSERT INTO public."projects" (
                "id_group", "code", "name", "json_settings"
            ) VALUES ($1, $2, $3, $4)
            RETURNING "id";
        ''', [
            self.id_group, self.code, self.name, self.json_settings
        ], with_result=True)

    @property
    def ID(self):
        return self['id']

    @ID.setter
    def ID(self, new_one):
        self['id'] = self.check_int(new_one, 'Идентификатор проекта')

    @property
    def id_group(self):
        return self['id_group']

    @id_group.setter
    def id_group(self, new_one):
        self['id_group'] = self.check_int(new_one, 'Идентификатор группы')

    @property
    def code(self):
        return self['code']

    @code.setter
    def code(self, new_one):
        self['code'] = self.check_str(new_one, 'Код проекта')

    @property
    def name(self):
        return self['name']

    @name.setter
    def name(self, new_one):
        self['name'] = self.check_str(new_one, arg='Имя проекта', allow_empty=True)

    @property
    def json_settings(self):
        return self['json_settings']

    @json_settings.setter
    def json_settings(self, new_one):
        # todo: валидация json-полей (по аналогии с check_str)
        self['json_settings'] = new_one

    @classmethod
    async def create(cls, group_id: int, data: dict) -> BaseItem:
        """Создание проекта.

        :param group_id: идентификатор родительской группы
        :param data:     данные проекта
        :rtype: entities.v1.Project
        """
        GLog.info('Создание проекта')
        data.update({'id_group': group_id})
        res = Project().load_from_json(data)
        await res._create()
        return res


class Projects(BaseList):
    """Список проектов.

    :param list data:   Данные для инициализации
    """

    ERR_PREFIX = 'Ошибка работы со списком слоев карты'

    def to_http(self) -> dict:
        """Возможность переопределить "базовую сериализацию" для HTTP."""
        return {
            "total": len(self),
            "data": self
        }

    @classmethod
    async def list(cls, group_id: int, include: list=None) -> BaseList:
        """Список проектов.

        :param group_id:    Идентификатор группы проектов (0 - все проекты)
        :param include:     Доп. параметры ответа
        :rtype entities.v1.Projects
        """
        GLog.info('Запрос списка проектов')

        include = include or []
        args = [group_id]
        GLog.debug('Запрос проектов: include=%s args=%s', include, args)

        pg = await create_pg_driver()
        if group_id == 0:
            sql = 'SELECT * FROM public."projects";'
            args = []
        else:
            sql = 'SELECT * FROM public."projects" WHERE id_group = $1;'
        return await pg.select(sql, args, list_type=cls, item_type=Project)
