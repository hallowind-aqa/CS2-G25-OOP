from src.models.category import CategoryNode
from src.models.budget import Budget


class TestCategoryNode:
    def test_create_node(self):
        node = CategoryNode("c1", "Food")
        assert node.category_id == "c1"
        assert node.name == "Food"
        assert node.parent_id is None
        assert node.children == []

    def test_set_parent_id(self):
        node = CategoryNode("c2", "Fruits", parent_id="c1")
        assert node.parent_id == "c1"

    def test_add_child(self):
        root = CategoryNode("1", "Root")
        child = CategoryNode("2", "Food")
        root.add_child(child)
        assert len(root.children) == 1
        assert root.children[0].category_id == "2"
        assert child.parent_id == "1"

    def test_add_multiple_children(self):
        root = CategoryNode("1", "Root")
        child1 = CategoryNode("2", "Food")
        child2 = CategoryNode("3", "Transport")
        root.add_child(child1)
        root.add_child(child2)
        assert len(root.children) == 2

    def test_nested_children(self):
        root = CategoryNode("1", "Root")
        food = CategoryNode("2", "Food")
        fruits = CategoryNode("3", "Fruits")
        food.add_child(fruits)
        root.add_child(food)
        assert len(root.children) == 1
        assert len(root.children[0].children) == 1
        assert root.children[0].children[0].name == "Fruits"

    def test_to_dict_basic(self):
        node = CategoryNode("1", "Root")
        d = node.to_dict()
        assert d["category_id"] == "1"
        assert d["name"] == "Root"
        assert d["parent_id"] is None
        assert d["children"] == []

    def test_to_dict_with_children(self):
        root = CategoryNode("1", "Root")
        food = CategoryNode("2", "Food")
        root.add_child(food)
        d = root.to_dict()
        assert len(d["children"]) == 1
        assert d["children"][0]["name"] == "Food"
        assert d["children"][0]["parent_id"] == "1"


class TestBudget:
    def test_create_budget(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0, 200.0)
        assert budget.budget_id == "b1"
        assert budget.category_id == "c1"
        assert budget.period == "2026-05"
        assert budget.limit_amount == 1000.0
        assert budget.spent_amount == 200.0

    def test_default_spent_amount(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0)
        assert budget.spent_amount == 0.0

    def test_remaining_amount(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0, 300.0)
        assert budget.remaining_amount() == 700.0

    def test_remaining_amount_zero(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0, 1000.0)
        assert budget.remaining_amount() == 0.0
        assert budget.is_over_budget() is False

    def test_is_over_budget_false(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0, 500.0)
        assert budget.is_over_budget() is False

    def test_is_over_budget_true(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0, 1200.0)
        assert budget.is_over_budget() is True

    def test_is_over_budget_exact_limit(self):
        budget = Budget("b1", "c1", "2026-05", 1000.0, 1000.0)
        assert budget.is_over_budget() is False