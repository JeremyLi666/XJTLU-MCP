from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class ProtocolStatus(str, Enum):
    """Status codes for protocol execution"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ProtocolRules:
    """
    Protocol rules governing message exchange between components
    
    This class enforces the communication rules defined by the MCP architecture,
    including timeouts, retry policies, and validation rules.
    """
    
    # Default timeout for protocol execution (seconds)
    DEFAULT_TIMEOUT = 30
    
    # Maximum number of retries for failed operations
    MAX_RETRIES = 3
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """Validate message conforms to protocol requirements"""
        required_fields = ["message_id", "sender", "receiver", "message_type", "intent"]
        return all(field in message for field in required_fields)
    
    @staticmethod
    def should_retry(status: ProtocolStatus, retry_count: int) -> bool:
        """Determine if operation should be retried based on status and count"""
        retryable_statuses = [ProtocolStatus.FAILED, ProtocolStatus.TIMEOUT]
        return status in retryable_statuses and retry_count < ProtocolRules.MAX_RETRIES
    
    @staticmethod
    def get_timeout(intent: str) -> int:
        """Get timeout duration based on intent type"""
        intent_timeouts = {
            "course_explanation": 20,
            "semester_planning": 45,  # Planning takes longer
            "career_alignment": 30,
            "prerequisite_check": 15,
            "workload_assessment": 25
        }
        return intent_timeouts.get(intent, ProtocolRules.DEFAULT_TIMEOUT)