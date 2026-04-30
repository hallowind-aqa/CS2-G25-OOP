from datetime import datetime, timezone

from src.managers.audit_manager import AuditManager
from src.models.audit import AuditBlock


def test_add_block_creates_genesis_block():
    manager = AuditManager()

    block = manager.add_block(
        operation_type="create_account",
        target_id="acc-1",
        payload_summary={"name": "Cash Wallet"},
    )

    assert block.index == 0
    assert block.previous_hash == "0"
    assert block.operation_type == "create_account"
    assert block.target_id == "acc-1"
    assert block.current_hash == block.calculate_hash()


def test_add_block_links_to_previous_hash():
    manager = AuditManager()
    first = manager.add_block("create_account", "acc-1", {"name": "Cash"})
    second = manager.add_block("update_account", "acc-1", {"name": "Daily Cash"})

    assert second.index == 1
    assert second.previous_hash == first.current_hash


def test_list_blocks_returns_blocks_in_order():
    manager = AuditManager()
    first = manager.add_block("create_account", "acc-1")
    second = manager.add_block("create_transaction", "tx-1")

    assert manager.list_blocks() == [first, second]
    assert manager.list_blocks() is not manager.blocks


def test_validate_chain_accepts_empty_chain():
    manager = AuditManager()

    assert manager.validate_chain() is True


def test_validate_chain_accepts_valid_chain():
    manager = AuditManager()
    manager.add_block("create_account", "acc-1", {"name": "Cash"})
    manager.add_block("create_transaction", "tx-1", {"amount": 100})

    assert manager.validate_chain() is True


def test_validate_chain_rejects_payload_tampering():
    manager = AuditManager()
    block = manager.add_block("create_transaction", "tx-1", {"amount": 100})

    block.payload_summary["amount"] = 999

    assert manager.validate_chain() is False


def test_validate_chain_rejects_operation_type_tampering():
    manager = AuditManager()
    block = manager.add_block("create_account", "acc-1")

    block.operation_type = "delete_account"

    assert manager.validate_chain() is False


def test_validate_chain_rejects_previous_hash_tampering():
    manager = AuditManager()
    manager.add_block("create_account", "acc-1")
    second = manager.add_block("create_transaction", "tx-1")

    second.previous_hash = "bad-hash"

    assert manager.validate_chain() is False


def test_validate_chain_rejects_genesis_previous_hash_tampering():
    manager = AuditManager()
    first = manager.add_block("create_account", "acc-1")

    first.previous_hash = "bad-hash"

    assert manager.validate_chain() is False


def test_audit_block_to_dict_and_from_dict_preserve_fields_and_hash():
    timestamp = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)
    block = AuditBlock(
        index=2,
        operation_type="delete_transaction",
        target_id="tx-1",
        payload_summary={"amount": 50},
        previous_hash="previous-hash",
        timestamp=timestamp,
    )

    restored = AuditBlock.from_dict(block.to_dict())

    assert restored.index == block.index
    assert restored.timestamp == block.timestamp
    assert restored.operation_type == block.operation_type
    assert restored.target_id == block.target_id
    assert restored.payload_summary == block.payload_summary
    assert restored.previous_hash == block.previous_hash
    assert restored.current_hash == block.current_hash
    assert restored.calculate_hash() == block.current_hash


def test_calculate_hash_does_not_depend_on_current_hash():
    block = AuditBlock(
        index=0,
        operation_type="create_account",
        target_id="acc-1",
        payload_summary={"name": "Cash"},
    )
    original_hash = block.calculate_hash()

    block.current_hash = "manually-changed"

    assert block.calculate_hash() == original_hash
