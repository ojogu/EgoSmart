# from beanie import Document
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from datetime import datetime, timezone


class CreateUser(BaseModel):
    whatsapp_phone_number: str
    whatsapp_profile_name: Optional[str] = None
    country_name: Optional[str] = None
    
    # country_name: Optional[str] = None
    # country_code : Optional[str] = None
    # country_dial_code: Optional[str] = None
    # country_flag: Optional[str] = None



class UserUpdate(BaseModel):
    email: EmailStr
    google_id: str
    email_verified: bool
    oauth_verified: bool
    picture: str
    first_name: str
    last_name: str
    onboarded: bool
    refresh_token: str
    access_token: str
    
# class CreateUser(BaseModel):
#     whatsapp_phone_number: str
#     country_name: Optional[str] = None
#     country_code: Optional[str] = None
#     email: Optional[EmailStr] = None
#     google_id: Optional[str] = None
#     email_verified: Optional[bool] = None
#     oauth_verified: Optional[bool] = None
#     picture: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     onboarded: Optional[bool] = None
#     refresh_token: Optional[str] = None
#     access_token: Optional[str] = None
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None




# # Input schema used by both agents
# class CountryInput(BaseModel):
#     country_number: str = Field(description="The phone number to country to get information about.")

# # Output schema ONLY for the second agent
# class CapitalInfoOutput(BaseModel):
#     country: str = Field(description="The country gotten.")
#     capital: str = Field(description="The capital city of the country.")
#     # Note: Population is illustrative; the LLM will infer or estimate this
#     # as it cannot use tools when output_schema is set.
#     population_estimate: str = Field(description="An estimated population of the capital city.")
