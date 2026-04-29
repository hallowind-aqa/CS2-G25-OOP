from src.data_structures.binary_search_tree import BinarySearchTree
from src.data_structures.doubly_linked_list import DoublyLinkedList
from src.data_structures.hash_table import HashTable
from src.data_structures.queue import Queue
from src.data_structures.stack import Stack
from src.data_structures.tree import Tree


def test_doubly_linked_list_append_prepend_and_traversal():
    linked_list = DoublyLinkedList()

    linked_list.append("B")
    linked_list.prepend("A")
    linked_list.append("C")

    assert linked_list.size == 3
    assert linked_list.to_list() == ["A", "B", "C"]
    assert linked_list.to_reversed_list() == ["C", "B", "A"]
    assert linked_list.traverse_forward() == "A <-> B <-> C"
    assert linked_list.traverse_backward() == "C <-> B <-> A"


def test_doubly_linked_list_remove_and_pop_head_tail():
    linked_list = DoublyLinkedList()
    for item in ["A", "B", "C"]:
        linked_list.append(item)

    assert linked_list.remove("B") == "B"
    assert linked_list.to_list() == ["A", "C"]
    assert linked_list.pop_head() == "A"
    assert linked_list.pop_tail() == "C"
    assert linked_list.pop_head() is None
    assert linked_list.size == 0


def test_stack_preserves_lifo_with_duplicate_values():
    stack = Stack()

    stack.push("A")
    stack.push("B")
    stack.push("A")

    assert stack.peek() == "A"
    assert stack.pop() == "A"
    assert stack.pop() == "B"
    assert stack.pop() == "A"
    assert stack.pop() is None
    assert stack.is_empty()


def test_queue_preserves_fifo_with_duplicate_values():
    queue = Queue()

    queue.enqueue("A")
    queue.enqueue("B")
    queue.enqueue("A")

    assert queue.peek() == "A"
    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert queue.dequeue() == "A"
    assert queue.dequeue() is None
    assert queue.is_empty()


def test_tree_supports_level_order_preorder_and_find():
    tree = Tree("Expense")
    food = Tree.add_child(tree.root, "Food")
    transport = Tree.add_child(tree.root, "Transport")
    Tree.add_child(food, "Grocery")
    Tree.add_child(food, "Restaurant")
    Tree.add_child(transport, "Bus")

    assert Tree.level_order(tree.root) == [
        "Expense",
        "Food",
        "Transport",
        "Grocery",
        "Restaurant",
        "Bus",
    ]
    assert Tree.preorder(tree.root) == [
        "Expense",
        "Food",
        "Grocery",
        "Restaurant",
        "Transport",
        "Bus",
    ]
    assert Tree.find(tree.root, "Restaurant").data == "Restaurant"
    assert Tree.find(tree.root, "Unknown") is None
    assert Tree.format_path(Tree.preorder(tree.root)) == (
        "Expense -> Food -> Grocery -> Restaurant -> Transport -> Bus"
    )


def test_binary_search_tree_supports_search_sort_and_range_query():
    bst = BinarySearchTree()
    transactions = [
        (50, "coffee"),
        (1200, "rent"),
        (200, "groceries"),
        (50, "snack"),
        (800, "salary bonus"),
    ]

    for amount, description in transactions:
        bst.insert(amount, description)

    assert bst.search(200) == "groceries"
    assert bst.search(999) is None
    assert bst.inorder_list() == ["coffee", "snack", "groceries", "salary bonus", "rent"]
    assert bst.range_query(100, 900) == ["groceries", "salary bonus"]
    assert bst.inorder() == "coffee -> snack -> groceries -> salary bonus -> rent"


def test_hash_table_put_update_remove_and_collision_handling():
    hash_table = HashTable(size=1)

    hash_table.put("account-1", "cash")
    hash_table.put("account-2", "bank")
    hash_table.put("account-1", "wallet")

    assert hash_table.get("account-1") == "wallet"
    assert hash_table.get("account-2") == "bank"
    assert hash_table.contains("account-2")
    assert hash_table.remove("account-2") == "bank"
    assert hash_table.get("account-2") is None
    assert not hash_table.contains("account-2")


def test_hash_table_rejects_invalid_size():
    try:
        HashTable(size=0)
    except ValueError as error:
        assert "positive" in str(error)
    else:
        raise AssertionError("HashTable should reject non-positive size")
