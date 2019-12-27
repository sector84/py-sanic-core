from core.base.v1 import BaseItem
from core.engine.v1 import (
    Checks,
    UnitTest,
)


class TestBaseItem(UnitTest):
    """."""

    def test___init__(self):
        """."""
        item = BaseItem()
        self.assertIsInstance(item, dict)
        self.assertIsInstance(item, Checks)
        self.assertTrue(hasattr(item, 'pg'))
        self.assertTrue(hasattr(item, 'load_from_json'))

        item = BaseItem({'ololo': 1})
        self.assertDictEqual(item, {'ololo': 1})

        item = BaseItem(ololo=1)
        self.assertDictEqual(item, {'ololo': 1})

        item = BaseItem([('ololo', 1), ('test', 'purpur')])
        self.assertDictEqual(item, {'ololo': 1, 'test': 'purpur'})
