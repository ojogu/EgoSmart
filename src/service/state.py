from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
import json


class RegistrationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RegistrationState:
    def __init__(self):
        self.status: RegistrationStatus = RegistrationStatus.NOT_STARTED
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.failed_at: Optional[str] = None
        self.failure_reason: Optional[str] = None
        self.progress_messages: List[str] = []
        self.steps_completed: List[str] = []

    def start(self):
        self.status = RegistrationStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.progress_messages.append("Registration started.")

    def complete(self):
        self.status = RegistrationStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.progress_messages.append("Registration completed.")

    def fail(self, reason: str):
        self.status = RegistrationStatus.FAILED
        self.failed_at = datetime.now(timezone.utc).isoformat()
        self.failure_reason = reason
        self.progress_messages.append(f"Failed: {reason}")

    def add_step(self, step: str):
        self.steps_completed.append(step)
        self.progress_messages.append(f"Step done: {step}")

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "failure_reason": self.failure_reason,
            "steps_completed": self.steps_completed,
            "progress_messages": self.progress_messages,
        }

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()
        instance.status = RegistrationStatus(data.get("status", "not_started"))
        instance.started_at = data.get("started_at")
        instance.completed_at = data.get("completed_at")
        instance.failed_at = data.get("failed_at")
        instance.failure_reason = data.get("failure_reason")
        instance.steps_completed = data.get("steps_completed", [])
        instance.progress_messages = data.get("progress_messages", [])
        return instance

# state = RegistrationState()

# Start registration
# user = User.query.get(user_id)
# state = user.get_registration_state()
# state.start()
# state.add_step("email_verified")
# user.update_registration_state(state)
# db.session.commit()

# # Later: mark complete
# state.complete()
# user.update_registration_state(state)
# db.session.commit()
