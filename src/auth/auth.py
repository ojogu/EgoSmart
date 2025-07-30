import logging
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from src.schemas.schema import CreateUser
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# from src.utils.logger import logger
from pathlib import Path
import json

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/auth.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)


auth_route = APIRouter(prefix="/auth")

@auth_route.get("/countries", response_class=JSONResponse)
def get_countries():
    json_file_path = Path(__file__).parent.parent / "utils" / "countries.json"

    if not json_file_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "Countries data not found"}
        )

    with open(json_file_path, "r", encoding="utf-8") as file:
        countries = json.load(file)

    return countries


@auth_route.post("/register")
async def register_user(data:dict, user_service = Depends(get_user_service)):
    try:
        existing_user = await user_service.get_user(full_number=data.full_number)
        if existing_user:
            logger.warning(f"User already exists: {data.full_number}")
            raise HTTPException(status_code=400, detail="User already exists")

        user_data = data.model_dump()
        result = await user_service.create_user(**user_data)
        logger.info(f"User registered successfully: {data.full_number}, user_id: {result}")

        return {
            "message": "User number successfully registered",
            # "user_id": str(result.inserted_id)
            "user_id": result
        }
    except HTTPException as http_exc:
        logger.error(f"HTTPException while registering user {data.full_number}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Exception while registering user {data.full_number}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")