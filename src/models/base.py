from datetime import datetime, timezone

class BaseRecord:
    """
    Base class for all business records in the system.
    Provides common fields and methods for inherited models.
    """

    # Initialize the base record.
    def __init__(self, entity_id=None):
        self.entity_id = entity_id # Unique identifier for the record, optional
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at

    # Update the updated_at timestamp to the current UTC time.
    def touch(self):
        self.updated_at = datetime.now(timezone.utc)

    # Convert the object to a JSON-serializable dictionary.
    def to_dict(self):
        return {
            "id": self.entity_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        # Dictionary containing core record fields