import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(f"postgresql+asyncpg://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
                             f"@{os.getenv('PG_HOST')}/{os.getenv('PG_DATABASE')}", pool_size=20, max_overflow=0)

AsyncSessionMaker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    with AsyncSessionMaker() as session:
        yield session
