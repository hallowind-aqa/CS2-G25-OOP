from datetime import datetime, timezone


class BaseRecord:
    def __init__(self, record_id=None):
        self.id = record_id
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at

    def touch(self):
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
