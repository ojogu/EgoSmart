from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class UserMessage(BaseModel):
    message: str = Field(..., description="Natural language message sent by the user")
    profile_name: str = Field(..., description="User's profile name")



class IntentItem(BaseModel):
    intent: Literal[
        "spend", 
        "earn", 
        "transfer", 
        "summary_request", 
        "upload", 
        "question", 
        "misc"
    ]
    amount: Optional[float] = None
    currency: Optional[str] = Field(None, description="Inferred from phone number unless explicitly stated")
    category: str = Field("uncategorized")
    description: str
    timestamp: str = Field("now")

class IntentResponse(BaseModel):
    intents: List[IntentItem]
