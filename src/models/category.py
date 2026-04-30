class CategoryNode:
    def __init__(self, category_id: str, name: str, parent_id: str = None):
        self.category_id = category_id
        self.name = name
        self.parent_id = parent_id
        self.children = []

    def add_child(self, child_node):
        """添加子分类节点"""
        child_node.parent_id = self.category_id
        self.children.append(child_node)

    def to_dict(self):
        """递归转为字典"""
        return {
            'category_id': self.category_id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children]
        }