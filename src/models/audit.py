import hashlib
import json
from datetime import datetime, timezone


class AuditBlock:
    def __init__(
        self,
        index,
        operation_type,
        target_id,
        payload_summary=None,
        previous_hash="0",
        timestamp=None,
        current_hash=None,
    ):
        self.index = index
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.operation_type = operation_type
        self.target_id = target_id
        self.payload_summary = {} if payload_summary is None else payload_summary
        self.previous_hash = previous_hash
        self.current_hash = current_hash or self.calculate_hash()

    def calculate_hash(self):
        payload = {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "operation_type": self.operation_type,
            "target_id": self.target_id,
            "payload_summary": self.payload_summary,
            "previous_hash": self.previous_hash,
        }
        encoded_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded_payload).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "operation_type": self.operation_type,
            "target_id": self.target_id,
            "payload_summary": self.payload_summary,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            operation_type=data["operation_type"],
            target_id=data["target_id"],
            payload_summary=data["payload_summary"],
            previous_hash=data["previous_hash"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            current_hash=data["current_hash"],
        )
