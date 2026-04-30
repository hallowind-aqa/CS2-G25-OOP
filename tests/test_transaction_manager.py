import pytest

from src.data_structures.binary_search_tree import BinarySearchTree
from src.data_structures.doubly_linked_list import DoublyLinkedList
from src.data_structures.hash_table import HashTable
from src.exceptions import (
    DuplicateRecordError,
    InsufficientFundsError,
    InvalidAmountError,
    RecordNotFoundError,
    ValidationError,
)
from src.managers.account_manager import AccountManager
from src.managers.transaction_manager import TransactionManager
from src.models.transaction import (
    ExpenseTransaction,
    IncomeTransaction,
    TransferTransaction,
)


def create_account_manager():
    account_manager = AccountManager()
    account_manager.create_account("cash", "Cash Wallet", "cash", balance=100)
    account_manager.create_account("bank", "Bank Account", "bank", balance=500)
    return account_manager


def create_transaction_manager():
    return TransactionManager(create_account_manager())


def test_transaction_manager_uses_required_data_structures():
    manager = create_transaction_manager()

    assert isinstance(manager.transactions, HashTable)
    assert isinstance(manager.amount_index, BinarySearchTree)
    assert isinstance(manager.timeline, DoublyLinkedList)


def test_add_income_transaction_updates_balance_and_index():
    manager = create_transaction_manager()
    transaction = IncomeTransaction("tx-1", 50, "cash", "Salary")

    added = manager.add_transaction(transaction)

    assert added is transaction
    assert manager.account_manager.get_account("cash").balance == 150
    assert manager.get_transaction("tx-1") is transaction


def test_add_expense_transaction_updates_balance():
    manager = create_transaction_manager()
    transaction = ExpenseTransaction("tx-1", 40, "cash", "Food")

    manager.add_transaction(transaction)

    assert manager.account_manager.get_account("cash").balance == 60


def test_add_transfer_transaction_updates_source_and_target_balances():
    manager = create_transaction_manager()
    transaction = TransferTransaction("tx-1", 80, "bank", "cash", "Transfer")

    manager.add_transaction(transaction)

    assert manager.account_manager.get_account("bank").balance == 420
    assert manager.account_manager.get_account("cash").balance == 180


def test_add_transaction_rejects_duplicate_id():
    manager = create_transaction_manager()
    manager.add_transaction(IncomeTransaction("tx-1", 50, "cash", "Salary"))

    with pytest.raises(DuplicateRecordError):
        manager.add_transaction(ExpenseTransaction("tx-1", 20, "cash", "Food"))


def test_get_transaction_rejects_unknown_id():
    manager = create_transaction_manager()

    with pytest.raises(RecordNotFoundError):
        manager.get_transaction("missing")


def test_delete_transaction_restores_balance_and_removes_from_hash_index():
    manager = create_transaction_manager()
    transaction = ExpenseTransaction("tx-1", 40, "cash", "Food")
    manager.add_transaction(transaction)

    deleted = manager.delete_transaction("tx-1")

    assert deleted is transaction
    assert manager.account_manager.get_account("cash").balance == 100
    with pytest.raises(RecordNotFoundError):
        manager.get_transaction("tx-1")


def test_delete_transaction_rejects_unknown_id():
    manager = create_transaction_manager()

    with pytest.raises(RecordNotFoundError):
        manager.delete_transaction("missing")


def test_list_transactions_returns_current_transactions():
    manager = create_transaction_manager()
    income = manager.add_transaction(IncomeTransaction("tx-1", 50, "cash", "Salary"))
    expense = manager.add_transaction(ExpenseTransaction("tx-2", 20, "cash", "Food"))

    assert set(manager.list_transactions()) == {income, expense}


def test_get_timeline_returns_forward_and_reverse_order():
    manager = create_transaction_manager()
    first = manager.add_transaction(IncomeTransaction("tx-1", 50, "cash", "Salary"))
    second = manager.add_transaction(ExpenseTransaction("tx-2", 20, "cash", "Food"))
    third = manager.add_transaction(TransferTransaction("tx-3", 30, "bank", "cash", "Transfer"))

    assert manager.get_timeline() == [first, second, third]
    assert manager.get_timeline(reverse=True) == [third, second, first]


def test_search_by_amount_range_returns_matching_current_transactions():
    manager = create_transaction_manager()
    small = manager.add_transaction(ExpenseTransaction("tx-1", 20, "cash", "Food"))
    medium = manager.add_transaction(IncomeTransaction("tx-2", 80, "cash", "Salary"))
    manager.add_transaction(TransferTransaction("tx-3", 200, "bank", "cash", "Transfer"))

    assert manager.search_by_amount_range(10, 100) == [small, medium]


def test_search_by_amount_range_filters_deleted_transactions():
    manager = create_transaction_manager()
    transaction = manager.add_transaction(IncomeTransaction("tx-1", 50, "cash", "Salary"))

    manager.delete_transaction("tx-1")

    assert transaction in manager.amount_index.range_query(50, 50)
    assert manager.search_by_amount_range(50, 50) == []


def test_update_transaction_replaces_transaction_and_updates_balance():
    manager = create_transaction_manager()
    old_transaction = manager.add_transaction(ExpenseTransaction("tx-1", 20, "cash", "Food"))

    new_transaction = manager.update_transaction(
        "tx-1",
        amount=60,
        category="Transport",
        description="Bus pass",
    )

    assert new_transaction is manager.get_transaction("tx-1")
    assert new_transaction is not old_transaction
    assert new_transaction.amount == 60
    assert new_transaction.category == "Transport"
    assert new_transaction.description == "Bus pass"
    assert manager.account_manager.get_account("cash").balance == 40
    assert manager.get_timeline() == [new_transaction]


def test_update_transaction_filters_old_amount_index_entry():
    manager = create_transaction_manager()
    old_transaction = manager.add_transaction(ExpenseTransaction("tx-1", 20, "cash", "Food"))

    new_transaction = manager.update_transaction("tx-1", amount=60)

    assert old_transaction in manager.amount_index.range_query(20, 20)
    assert manager.search_by_amount_range(20, 20) == []
    assert manager.search_by_amount_range(60, 60) == [new_transaction]


def test_update_transfer_transaction_updates_accounts_and_balances():
    manager = create_transaction_manager()
    manager.add_transaction(TransferTransaction("tx-1", 30, "bank", "cash", "Transfer"))

    updated = manager.update_transaction("tx-1", amount=50)

    assert isinstance(updated, TransferTransaction)
    assert manager.account_manager.get_account("bank").balance == 450
    assert manager.account_manager.get_account("cash").balance == 150


def test_update_transaction_rejects_unknown_id():
    manager = create_transaction_manager()

    with pytest.raises(RecordNotFoundError):
        manager.update_transaction("missing", amount=20)


def test_update_transaction_failure_restores_old_balance_and_index():
    manager = create_transaction_manager()
    old_transaction = manager.add_transaction(ExpenseTransaction("tx-1", 20, "cash", "Food"))

    with pytest.raises(InsufficientFundsError):
        manager.update_transaction("tx-1", amount=200)

    assert manager.account_manager.get_account("cash").balance == 80
    assert manager.get_transaction("tx-1") is old_transaction
    assert manager.get_timeline() == [old_transaction]
    assert manager.search_by_amount_range(20, 20) == [old_transaction]
    assert manager.search_by_amount_range(200, 200) == []


def test_search_by_amount_range_rejects_negative_bounds():
    manager = create_transaction_manager()

    with pytest.raises(InvalidAmountError):
        manager.search_by_amount_range(-1, 100)


def test_search_by_amount_range_rejects_reversed_bounds():
    manager = create_transaction_manager()

    with pytest.raises(ValidationError):
        manager.search_by_amount_range(100, 10)
