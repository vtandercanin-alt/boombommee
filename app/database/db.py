from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import config
from app.models.models import Base


class Database:
    """Database connection and session management"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.async_session = None
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        kwargs = {}
        if self.database_url.startswith("sqlite"):
            # SQLite: no pool args, allow cross-thread access, enable WAL
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            # PostgreSQL: connection pool
            kwargs["pool_size"] = 20
            kwargs["max_overflow"] = 0

        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            **kwargs,
        )

        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Enable WAL for SQLite (better concurrency)
        if self.database_url.startswith("sqlite"):
            async with self.engine.begin() as conn:
                await conn.exec_driver_sql("PRAGMA journal_mode=WAL;")

        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncSession:
        """Get async session"""
        if self.async_session is None:
            await self.initialize()
        return self.async_session()
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()


# Global database instance
db = Database(config.DATABASE_URL)


async def get_session() -> AsyncSession:
    """Dependency to get session"""
    return await db.get_session()
