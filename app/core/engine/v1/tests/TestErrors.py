from core.engine.v1 import (
    Error,
    Errors,
    UnitTest
)


class TestErrors(UnitTest):
    """."""

    def test_errors(self):
        """."""
        try:
            Errors.error(
                'сообщение', status=402, code=100500, data={'test': 1},
            )
        except Error as error:
            self.assertEqual(error.code, 100500)
            self.assertEqual(error.status, 402)
            self.assertEqual(error.data, {'test': 1})
            self.assertEqual(error.message, 'Ошибка: сообщение')
            self.assertEqual(str(error), '[402] Ошибка: сообщение')
            self.assertDictEqual(error.to_dict(), {
                'code': 100500,
                'name': 'Ошибка: сообщение',
                'descr': {'test': 1},
            })

        test = Errors.expect(['123', '45'], 'сообщение')
        self.assertEqual(test, ['123', '45'])

        try:
            Errors.expect(
                {}, 'сообщение', status=402,
                code=100500, data={'test': 1},
            )
        except Error as error:
            self.assertEqual(error.code, 100500)
            self.assertEqual(error.status, 402)
            self.assertEqual(error.data, {'test': 1})
            self.assertEqual(error.message, 'Ошибка: сообщение')
            self.assertEqual(str(error), '[402] Ошибка: сообщение')
            self.assertDictEqual(error.to_dict(), {
                'code': 100500,
                'name': 'Ошибка: сообщение',
                'descr': {'test': 1},
            })
