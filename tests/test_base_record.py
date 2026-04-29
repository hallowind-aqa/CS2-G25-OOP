from src.models.base import BaseRecord


def test_create_base_record():
    record = BaseRecord()

    assert record is not None


def test_create_base_record_with_id():
    record = BaseRecord(record_id=1001)

    assert record.id == 1001


def test_time_fields_are_initialized():
    record = BaseRecord()

    assert record.created_at is not None
    assert record.updated_at is not None
    assert record.created_at == record.updated_at


def test_touch_updates_updated_at():
    record = BaseRecord()
    old_updated_at = record.updated_at

    record.touch()

    assert record.updated_at > old_updated_at
    assert record.created_at < record.updated_at


def test_to_dict_returns_serializable_base_fields():
    record = BaseRecord(record_id=2002)
    result = record.to_dict()

    assert result == {
        "id": 2002,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }
