import sys
import asyncio
import argparse

# Нужно отрегулировать путь импортов, чтобы работали импорт нашей логики
sys.path.append('/app')
from sys_scripts.DatabaseCreate import AppDatabase
from sys_scripts.DatabasePopulate import AppDatabasePopulate


async def create_db(name):
    async with AppDatabase(name) as db:
        await db.create()

    async with AppDatabasePopulate(name) as db:
        await db.populate()


if __name__ != '__main__':
    raise Exception('Запрещено импортировать файл')

# Получаем аргументы запуска из командной строки
_parser = argparse.ArgumentParser(
    description='Скрипт инициализации базы данных сервера rest-mock'
)
_parser.add_argument(
    'name', metavar='DB_NAME', type=str, help='Имя БД приложения'
)

_args = _parser.parse_args()
loop = asyncio.get_event_loop()
loop.run_until_complete(create_db(_args.name))
loop.close()

