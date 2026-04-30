from src.models.audit import AuditBlock


class AuditManager:
    def __init__(self):
        self.blocks = []

    def add_block(self, operation_type, target_id, payload_summary=None):
        previous_hash = "0" if not self.blocks else self.blocks[-1].current_hash
        block = AuditBlock(
            index=len(self.blocks),
            operation_type=operation_type,
            target_id=target_id,
            payload_summary=payload_summary,
            previous_hash=previous_hash,
        )
        self.blocks.append(block)
        return block

    def validate_chain(self):
        for index, block in enumerate(self.blocks):
            if block.current_hash != block.calculate_hash():
                return False
            if index == 0:
                if block.previous_hash != "0":
                    return False
            elif block.previous_hash != self.blocks[index - 1].current_hash:
                return False
        return True

    def list_blocks(self):
        return list(self.blocks)
