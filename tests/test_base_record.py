import unittest
from src.models.base import BaseRecord

class TestBaseRecord(unittest.TestCase):

    # Test that a BaseRecord instance can be created successfully.
    def test_create_base_record(self):
        record = BaseRecord()
        self.assertIsNotNone(record)

    #Test creating a record with a specified ID.
    def test_create_with_id(self):
        record = BaseRecord(record_id=1001)
        self.assertEqual(record.id, 1001)

    #Test created_at and updated_at are set correctly on initialization.
    def test_time_fields_init(self):
        record = BaseRecord()
        self.assertIsNotNone(record.created_at)
        self.assertIsNotNone(record.updated_at)
        self.assertEqual(record.created_at, record.updated_at)

    #Test that touch() updates the updated_at timestamp.
    def test_touch_update_time(self):
        record = BaseRecord()
        old_updated_time = record.updated_at

        import time
        time.sleep(0.001)

        record.touch()
        self.assertGreater(record.updated_at, old_updated_time)
        self.assertLess(record.created_at, record.updated_at)

    #Test to_dict() returns a valid, serializable dictionary.
    def test_to_dict_return_dict(self):
        record = BaseRecord(record_id=2002)
        result = record.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], 2002)
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)
        self.assertIsInstance(result["created_at"], str)
        self.assertIsInstance(result["updated_at"], str)


if __name__ == '__main__':
    unittest.main()