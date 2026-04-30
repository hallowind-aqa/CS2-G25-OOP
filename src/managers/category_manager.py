from src.data_structures.tree import Tree
from src.exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError
from src.models.category import CategoryNode
from src.models.transaction import ExpenseTransaction


class CategoryManager:
    def __init__(self, transaction_manager=None):
        self.root_id = "root"
        self.category_tree = Tree(self.root_id)
        self.categories = {}
        self.transaction_manager = transaction_manager

    def create_category(self, category_id, name, parent_id=None):
        if not category_id or not name:
            raise ValidationError("Category ID and name are required")
        if category_id in self.categories or category_id == self.root_id:
            raise DuplicateRecordError(f"Category already exists: {category_id}")

        effective_parent_id = self.root_id if parent_id is None else parent_id
        parent_node = Tree.find(self.category_tree.root, effective_parent_id)
        if parent_node is None:
            raise RecordNotFoundError(f"Category not found: {effective_parent_id}")

        category = CategoryNode(category_id, name, parent_id)
        Tree.add_child(parent_node, category_id)
        self.categories[category_id] = category

        if parent_id is not None:
            self.categories[parent_id].add_child(category)

        return category

    def find_category(self, category_id):
        node = Tree.find(self.category_tree.root, category_id)
        if node is None or category_id == self.root_id:
            raise RecordNotFoundError(f"Category not found: {category_id}")
        return self.categories[category_id]

    def list_categories(self):
        category_ids = Tree.preorder(self.category_tree.root)
        return [
            self.categories[category_id]
            for category_id in category_ids
            if category_id != self.root_id
        ]

    def calculate_category_spending(self, category_id, transaction_manager=None):
        self.find_category(category_id)
        node = Tree.find(self.category_tree.root, category_id)
        category_ids = set(Tree.preorder(node))
        manager = transaction_manager or self.transaction_manager
        if manager is None:
            raise ValidationError("TransactionManager is required")

        total = 0
        for transaction in manager.list_transactions():
            if (
                isinstance(transaction, ExpenseTransaction)
                and transaction.category in category_ids
            ):
                total += transaction.amount
        return total
