from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
from fastapi import status
from src.base.schema import SuccessResponse

# Constants for error messages
EMAIL_IN_USE = "This email is already in use."
NOT_FOUND = "Not found!"
ID_OR_UNIQUE_ID_REQUIRED = "ID or Unique ID required!"
INVALID_CREDENTIALS = "Invalid Credentials!"
COULD_NOT_VALIDATE_CRED = "Could not validate credentials."
SUCCESS = "Success"
EXPIRED = "Token expired."
SERVER_ERROR = "An error occurred on the server"

class FastAPICustomResponse:
    """Custom response class for consistent FastAPI responses"""
    
    def success_response(
        self,
        role: Optional[str] = None,
        message: str = SUCCESS,
        data: Optional[Any] = None,
        status_code: int = status.HTTP_200_OK,
        headers: Optional[Dict[str, str]] = None,
    ) -> JSONResponse:
        """Create a success response, validating data with a Pydantic schema"""
        validated_data = SuccessResponse(
            role=role,
            message=message,
            data=data,
            status_code=status_code,
            headers=headers
        )
        return JSONResponse(
            content=validated_data.model_dump(),
            status_code=validated_data.status_code,
            headers=headers
        )


    
    # Additional FastAPI-specific methods
    def created_response(
        self,
        message: str = "Resource created successfully",
        data: Optional[Any] = None,
        role: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> JSONResponse:
        """201 Created"""
        return self._create_response(
            'success', message, data, status.HTTP_201_CREATED, role, headers
        )
    
    def accepted_response(
        self,
        message: str = "Request accepted",
        data: Optional[Any] = None,
        role: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> JSONResponse:
        """202 Accepted"""
        return self._create_response(
            'success', message, data, status.HTTP_202_ACCEPTED, role, headers
        )
    
    def no_content_response(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> JSONResponse:
        """204 No Content"""
        return JSONResponse(
            content=None,
            status_code=status.HTTP_204_NO_CONTENT,
            headers=headers
        )

# Single instance for import
custom_response = FastAPICustomResponse()

# Example usage in FastAPI routes:
"""
from fastapi import FastAPI
from custom_response import custom_response

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Simulate user lookup
    if user_id == 1:
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        return custom_response.success_response(
            message="User retrieved successfully",
            data=user_data,
            role="user"
        )
    else:
        return custom_response.not_found_error("User not found")

@app.post("/users")
async def create_user(user_data: dict):
    # Simulate user creation
    if "email" in user_data and user_data["email"] == "existing@example.com":
        return custom_response.email_in_use_error()
    
    # Create user logic here
    new_user = {"id": 2, "name": user_data.get("name"), "email": user_data.get("email")}
    return custom_response.created_response(
        message="User created successfully",
        data=new_user,
        role="user"
    )
"""