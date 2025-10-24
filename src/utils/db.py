
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import config
from src.base.model import Base
from .config import config
from src.model.user import User

engine = create_async_engine(url= config.DATABASE_URL)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates and yields an asynchronous database session.

    This function is an asynchronous generator that creates a new database session
    using the async_session factory and yields it. The session is automatically
    closed when the generator is exhausted or the context is exited.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session object.

    Usage:
        async for session in get_session():
            # Use the session for database operations
            ...
    """
    async with async_session() as session:
        yield session


async def init_db():
    """
    Initialize the database by creating all tables defined in the Base metadata.

    This asynchronous function uses the SQLAlchemy engine to create all tables
    that are defined in the Base metadata. It's typically used when setting up
    the database for the first time or after a complete reset.

    The function uses a connection from the engine and runs the create_all
    method synchronously within the asynchronous context.
    """
    async with engine.begin() as conn:
        # Use run_sync to call the synchronous create_all method in an async context
        await conn.run_sync(Base.metadata.create_all)
        print(Base.metadata.tables.keys())

async def drop_db():
    """
    Drop all tables in the database.

    This asynchronous function uses the SQLAlchemy engine to drop all tables
    that are defined in the Base metadata. It's typically used when you want
    to completely reset the database structure.

    Caution: This operation will delete all data in the tables. Use with care.
    """
    async with engine.begin() as conn:
        # Drop tables in reverse order to handle dependencies, using CASCADE
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE;"))
        print("All tables dropped with CASCADE.")




# from motor.motor_asyncio import AsyncIOMotorClient
# from src.utils.config import config
# from beanie import init_beanie
# from src.schemas.schema import User, Transaction, Conversation_states, Uploads, Intents_log, AgentSchema

# MONGO_URL = config.DATABASE_URL  


# # Optional: make db accessible in FastAPI app
# async def init_db():
#     client = AsyncIOMotorClient(MONGO_URL)
#     db =  client.egosmart_db 
#     await init_beanie(database=db, document_models=[User, Transaction, Conversation_states, Uploads, Intents_log, AgentSchema])

# async def reset_db():
#     # Connect to the MongoDB server
#     client = AsyncIOMotorClient(MONGO_URL)
#     db =  client.egosmart_db 
#     # Drop the database
#     await client.drop_database(db)
#     print(f"✅ Dropped DB: {db}")
    
# async def init_indexes():
#     client = AsyncIOMotorClient(MONGO_URL)
#     db =  client.egosmart_db 
#     await db.users.create_index("phone_number", unique=True)
#     indexes = await db.users.index_information()
#     print(indexes)
