from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class MCPMessage(BaseModel):
    """
    Standardized message format for MCP architecture
    
    This class defines the contract for all inter-component communication
    within the system, ensuring protocol consistency across modules.
    """
    message_id: str = Field(..., description="Unique identifier for the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was created")
    sender: str = Field(..., description="Component that sent the message")
    receiver: str = Field(..., description="Intended recipient component")
    message_type: str = Field(..., description="Type of message (request, response, event)")
    intent: str = Field(..., description="User's intended action or query type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message content/data")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_123456",
                "timestamp": "2025-01-12T14:30:00Z",
                "sender": "web_interface",
                "receiver": "dispatcher",
                "message_type": "request",
                "intent": "course_explanation",
                "payload": {
                    "query": "Explain finance courses",
                    "subject_keywords": ["fin"]
                },
                "context": {
                    "user_profile": {
                        "major": "Economics",
                        "target_program": "HKU MFWM"
                    }
                }
            }
        }