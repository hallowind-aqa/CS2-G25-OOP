from src.data_structures.binary_search_tree import BinarySearchTree
from src.data_structures.doubly_linked_list import DoublyLinkedList
from src.data_structures.hash_table import HashTable
from src.exceptions import (
    DuplicateRecordError,
    InvalidAmountError,
    RecordNotFoundError,
    ValidationError,
)
from src.models.transaction import (
    ExpenseTransaction,
    IncomeTransaction,
    TransferTransaction,
)


class TransactionManager:
    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.transactions = HashTable()
        self.amount_index = BinarySearchTree()
        self.timeline = DoublyLinkedList()

    def add_transaction(self, transaction):
        if self.transactions.contains(transaction.transaction_id):
            raise DuplicateRecordError(
                f"Transaction already exists: {transaction.transaction_id}"
            )

        transaction.apply(self.account_manager.accounts)
        self._store_transaction(transaction)
        return transaction

    def get_transaction(self, transaction_id):
        transaction = self.transactions.get(transaction_id)
        if transaction is None:
            raise RecordNotFoundError(f"Transaction not found: {transaction_id}")
        return transaction

    def update_transaction(
        self,
        transaction_id,
        amount=None,
        category=None,
        description=None,
        date=None,
        account_id=None,
        source_account_id=None,
        target_account_id=None,
    ):
        old_transaction = self.get_transaction(transaction_id)
        new_transaction = self._build_updated_transaction(
            old_transaction=old_transaction,
            amount=amount,
            category=category,
            description=description,
            date=date,
            account_id=account_id,
            source_account_id=source_account_id,
            target_account_id=target_account_id,
        )

        old_transaction.revert(self.account_manager.accounts)
        try:
            new_transaction.apply(self.account_manager.accounts)
        except Exception:
            old_transaction.apply(self.account_manager.accounts)
            raise

        self.transactions.put(transaction_id, new_transaction)
        self.timeline.remove(old_transaction)
        self.timeline.append(new_transaction)
        self.amount_index.insert(new_transaction.amount, new_transaction)
        return new_transaction

    def delete_transaction(self, transaction_id):
        transaction = self.get_transaction(transaction_id)
        transaction.revert(self.account_manager.accounts)
        self.transactions.remove(transaction_id)
        self.timeline.remove(transaction)
        return transaction

    def list_transactions(self):
        transactions = []
        for bucket in self.transactions.table:
            for _, transaction in bucket:
                transactions.append(transaction)
        return transactions

    def search_by_amount_range(self, minimum, maximum):
        if minimum < 0 or maximum < 0:
            raise InvalidAmountError("Amount range cannot be negative")
        if minimum > maximum:
            raise ValidationError("Minimum amount cannot exceed maximum amount")

        candidates = self.amount_index.range_query(minimum, maximum)
        return [
            transaction
            for transaction in candidates
            if self.transactions.get(transaction.transaction_id) is transaction
        ]

    def get_timeline(self, reverse=False):
        if reverse:
            return self.timeline.to_reversed_list()
        return self.timeline.to_list()

    def _store_transaction(self, transaction):
        self.transactions.put(transaction.transaction_id, transaction)
        self.amount_index.insert(transaction.amount, transaction)
        self.timeline.append(transaction)

    def _build_updated_transaction(
        self,
        old_transaction,
        amount=None,
        category=None,
        description=None,
        date=None,
        account_id=None,
        source_account_id=None,
        target_account_id=None,
    ):
        if isinstance(old_transaction, IncomeTransaction):
            return IncomeTransaction(
                transaction_id=old_transaction.transaction_id,
                amount=old_transaction.amount if amount is None else amount,
                account_id=old_transaction.account_id if account_id is None else account_id,
                category=old_transaction.category if category is None else category,
                description=(
                    old_transaction.description
                    if description is None
                    else description
                ),
                date=old_transaction.date if date is None else date,
            )

        if isinstance(old_transaction, ExpenseTransaction):
            return ExpenseTransaction(
                transaction_id=old_transaction.transaction_id,
                amount=old_transaction.amount if amount is None else amount,
                account_id=old_transaction.account_id if account_id is None else account_id,
                category=old_transaction.category if category is None else category,
                description=(
                    old_transaction.description
                    if description is None
                    else description
                ),
                date=old_transaction.date if date is None else date,
            )

        if isinstance(old_transaction, TransferTransaction):
            return TransferTransaction(
                transaction_id=old_transaction.transaction_id,
                amount=old_transaction.amount if amount is None else amount,
                source_account_id=(
                    old_transaction.source_account_id
                    if source_account_id is None
                    else source_account_id
                ),
                target_account_id=(
                    old_transaction.target_account_id
                    if target_account_id is None
                    else target_account_id
                ),
                category=old_transaction.category if category is None else category,
                description=(
                    old_transaction.description
                    if description is None
                    else description
                ),
                date=old_transaction.date if date is None else date,
            )

        raise ValidationError("Unsupported transaction type")
