import unittest
import contextlib

from core.engine.v1 import Error


class UnitTest(unittest.TestCase):
    """Базовый класс для всех юнит-тестов фреймворка."""

    maxDiff = 4096

    # Пока что не нужны
    # @classmethod
    # def setUpClass(cls):
    #     """."""
    #     # todo:
    #     pass
    #
    # def setUp(self):
    #     """."""
    #     # todo:
    #     pass
    #
    # def tearDown(self):
    #     """."""
    #     # todo:
    #     pass

    def shortDescription(self):
        """Функция автоматического форматирования nosetests."""
        _cls = self.__class__.__name__.replace('Test', '')
        _fnc = self._testMethodName.replace('test_', '')
        return '%s.%s' % (_cls, _fnc)

    def assertError(self, regex, status=500):
        """Функция проверки ошибки core.Error."""
        @contextlib.contextmanager
        def mgr():
            failed = True
            try:
                yield
                failed = False
            except Error as err:
                arg = (status, err.status)
                tpl = 'Ожидалась ошибка со статусом [%s], но получен [%s]'
                self.assertEqual(err.status, status, msg=tpl % arg)
                msg = 'Не совпадает сообщение об ошибке'
                self.assertRegex(str(err), regex, msg=msg)
            except Exception as exp:
                tpl = 'Ожидалась ошибка core.engine.v1.Error, но получена %s'
                raise Exception(tpl % repr(exp))
            msg = 'Все прошло слишком гладко! Нужна ошибка с текстом "%s"'
            self.assertTrue(failed, msg=msg % regex)
        return mgr()
