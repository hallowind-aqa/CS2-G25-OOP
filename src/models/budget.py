class Budget:
    def __init__(self, budget_id: str, category_id: str, period: str, 
                 limit_amount: float, spent_amount: float = 0.0):
        self.budget_id = budget_id
        self.category_id = category_id
        self.period = period
        self.limit_amount = limit_amount
        self.spent_amount = spent_amount

    def remaining_amount(self) -> float:
        """计算剩余预算"""
        return self.limit_amount - self.spent_amount

    def is_over_budget(self) -> bool:
        """判断是否超预算"""
        return self.remaining_amount() <= 0