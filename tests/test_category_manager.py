import pytest

from src.data_structures.tree import Tree
from src.exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError
from src.managers.account_manager import AccountManager
from src.managers.category_manager import CategoryManager
from src.managers.transaction_manager import TransactionManager
from src.models.category import CategoryNode
from src.models.transaction import (
    ExpenseTransaction,
    IncomeTransaction,
    TransferTransaction,
)


def create_transaction_manager():
    account_manager = AccountManager()
    account_manager.create_account("cash", "Cash Wallet", "cash", balance=500)
    account_manager.create_account("bank", "Bank Account", "bank", balance=1000)
    return TransactionManager(account_manager)


def test_category_manager_uses_tree():
    manager = CategoryManager()

    assert isinstance(manager.category_tree, Tree)
    assert manager.category_tree.root.data == "root"


def test_create_root_level_category():
    manager = CategoryManager()

    category = manager.create_category("food", "Food")

    assert isinstance(category, CategoryNode)
    assert category.category_id == "food"
    assert category.name == "Food"
    assert category.parent_id is None
    assert Tree.find(manager.category_tree.root, "food") is not None


def test_create_child_category():
    manager = CategoryManager()
    parent = manager.create_category("food", "Food")

    child = manager.create_category("restaurant", "Restaurant", parent_id="food")

    assert child.parent_id == "food"
    assert parent.children == [child]
    assert Tree.find(manager.category_tree.root, "restaurant") is not None


def test_create_nested_categories():
    manager = CategoryManager()
    manager.create_category("expense", "Expense")
    manager.create_category("food", "Food", parent_id="expense")
    manager.create_category("restaurant", "Restaurant", parent_id="food")

    assert [category.category_id for category in manager.list_categories()] == [
        "expense",
        "food",
        "restaurant",
    ]


def test_create_category_rejects_duplicate_id():
    manager = CategoryManager()
    manager.create_category("food", "Food")

    with pytest.raises(DuplicateRecordError):
        manager.create_category("food", "Food Again")


def test_create_category_rejects_missing_parent():
    manager = CategoryManager()

    with pytest.raises(RecordNotFoundError):
        manager.create_category("restaurant", "Restaurant", parent_id="missing")


@pytest.mark.parametrize("category_id,name", [("", "Food"), (None, "Food"), ("food", ""), ("food", None)])
def test_create_category_rejects_empty_id_or_name(category_id, name):
    manager = CategoryManager()

    with pytest.raises(ValidationError):
        manager.create_category(category_id, name)


def test_find_category_returns_category():
    manager = CategoryManager()
    category = manager.create_category("food", "Food")

    assert manager.find_category("food") is category


def test_find_category_rejects_unknown_category():
    manager = CategoryManager()

    with pytest.raises(RecordNotFoundError):
        manager.find_category("missing")


def test_find_category_rejects_root():
    manager = CategoryManager()

    with pytest.raises(RecordNotFoundError):
        manager.find_category("root")


def test_list_categories_returns_preorder_without_root():
    manager = CategoryManager()
    manager.create_category("expense", "Expense")
    manager.create_category("food", "Food", parent_id="expense")
    manager.create_category("transport", "Transport", parent_id="expense")

    assert [category.category_id for category in manager.list_categories()] == [
        "expense",
        "food",
        "transport",
    ]


def test_calculate_category_spending_includes_child_categories():
    transaction_manager = create_transaction_manager()
    category_manager = CategoryManager(transaction_manager)
    category_manager.create_category("food", "Food")
    category_manager.create_category("restaurant", "Restaurant", parent_id="food")
    category_manager.create_category("grocery", "Grocery", parent_id="food")

    transaction_manager.add_transaction(ExpenseTransaction("tx-1", 40, "cash", "restaurant"))
    transaction_manager.add_transaction(ExpenseTransaction("tx-2", 60, "cash", "grocery"))

    assert category_manager.calculate_category_spending("food") == 100


def test_calculate_category_spending_excludes_income_transfer_and_other_categories():
    transaction_manager = create_transaction_manager()
    category_manager = CategoryManager(transaction_manager)
    category_manager.create_category("food", "Food")
    category_manager.create_category("restaurant", "Restaurant", parent_id="food")
    category_manager.create_category("transport", "Transport")

    transaction_manager.add_transaction(ExpenseTransaction("tx-1", 40, "cash", "restaurant"))
    transaction_manager.add_transaction(ExpenseTransaction("tx-2", 30, "cash", "transport"))
    transaction_manager.add_transaction(IncomeTransaction("tx-3", 100, "cash", "restaurant"))
    transaction_manager.add_transaction(TransferTransaction("tx-4", 50, "bank", "cash", "restaurant"))

    assert category_manager.calculate_category_spending("food") == 40


def test_calculate_category_spending_uses_current_transactions_only():
    transaction_manager = create_transaction_manager()
    category_manager = CategoryManager(transaction_manager)
    category_manager.create_category("food", "Food")

    transaction_manager.add_transaction(ExpenseTransaction("tx-1", 40, "cash", "food"))
    transaction_manager.delete_transaction("tx-1")

    assert category_manager.calculate_category_spending("food") == 0


def test_calculate_category_spending_accepts_transaction_manager_argument():
    transaction_manager = create_transaction_manager()
    category_manager = CategoryManager()
    category_manager.create_category("food", "Food")
    transaction_manager.add_transaction(ExpenseTransaction("tx-1", 40, "cash", "food"))

    assert category_manager.calculate_category_spending("food", transaction_manager) == 40


def test_calculate_category_spending_rejects_missing_transaction_manager():
    category_manager = CategoryManager()
    category_manager.create_category("food", "Food")

    with pytest.raises(ValidationError):
        category_manager.calculate_category_spending("food")


def test_calculate_category_spending_rejects_unknown_category():
    category_manager = CategoryManager(create_transaction_manager())

    with pytest.raises(RecordNotFoundError):
        category_manager.calculate_category_spending("missing")
