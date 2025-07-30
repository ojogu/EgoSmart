import uuid
import httpx
import datetime
from src.model.user import User, Agent
import logging
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.base.exception import (
    NotVerified
)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/agent.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

class AgentService():
    def __init__(self, db: AsyncSession):
        self.db = db


    def create_session_id(self) -> str:
        """
        Generates a short unique reference ID.

        Returns:
            str: A short unique reference ID.
        """
        return uuid.uuid4().hex[:8]




    async def get_session(self, whatsapp_phone_number: str):
        pass 










# async def save_message(user_id: str, session_id: str, message: str, role: str):
#     try:
#         await AgentSchema.find(AgentSchema.user_id == user_id).upsert(
#             on_insert=AgentSchema(
#                 user_id=user_id,
#                 messages=[{
#                     "session_id": session_id,
#                     "content": message,
#                     "role": role,
#                     "timestamp": datetime.datetime.now(datetime.timezone.utc)
#                 }]
#             ),
#             on_update={
#                 "$push": {
#                     "messages": {
#                         "session_id": session_id,
#                         "content": message,
#                         "role": role,
#                         "timestamp": datetime.datetime.now(datetime.timezone.utc)
#                     }
#                 }
#             }
#         )
#         logger.info(f"Saved message for user_id: {user_id}, session_id: {session_id}, role: {role}")
#     except Exception as e:
#         logger.error(f"Error saving message for user_id {user_id}, session_id {session_id}: {e}")
#         raise


# async def get_or_create_session(user_id: str) -> str:
#     try:
#         session = await AgentSchema.find_one(
#             AgentSchema.user_id == user_id,
#             AgentSchema.active == True
#         )
#         if session:
#             logger.info(f"Found active session for user_id: {user_id}, session_id: {session.session_id}")
#             return session.session_id

#         session_id = create_session_id()
#         logger.info(f"Creating new session for user_id: {user_id}, session_id: {session_id}")

#         # No external request, just create and insert the session
#         new_session = AgentSchema(
#             session_id=session_id,
#             user_id=user_id,
#             agent_name="my_sample_agent",
#             created_at=datetime.datetime.now(datetime.timezone.utc),
#             active=True,
#             state={},
#             messages=[]
#         )
#         await new_session.insert()
#         logger.info(f"Inserted new session document for user_id: {user_id}, session_id: {session_id}")

#         return session_id
#     except Exception as e:
#         logger.error(f"Error in get_or_create_session for user_id {user_id}: {e}")
#         raise


# # async def ask_agent(user_id: str, session_id: str, message: str):
# #     try:
# #         logger.info(f"Asking agent for user_id: {user_id}, session_id: {session_id}, message: {message}")
# #         async with httpx.AsyncClient() as client:
# #             response = await client.post(
# #                 "http://localhost:5000/run",

# #                 json={
# #                     "app_name": "my_sample_agent",
# #                     "user_id": user_id,
# #                     "session_id": session_id,
# #                     "new_message": {
# #                         "role": "user",
# #                         "parts": [{"text": message}]
# #                     }
# #                 }
# #             )
# #         logger.info(f"Agent response status: {response.status_code} for user_id: {user_id}, session_id: {session_id}")
# #         logger.info(response)
# #         return response.json()
# #     except Exception as e:
# #         logger.error(f"Agent request failed for user_id {user_id}, session_id {session_id}: {e}")
# #         raise RuntimeError(f"Agent request failed: {e}")