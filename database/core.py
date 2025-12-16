import aiosqlite
from typing import Optional

class DatabaseCore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def execute(self, query: str, params: tuple = ()):
        if not self.conn:
            raise RuntimeError("Database not connected")
        return await self.conn.execute(query, params)

    async def executemany(self, query: str, params_list):
        if not self.conn:
            raise RuntimeError("Database not connected")
        return await self.conn.executemany(query, params_list)

    async def commit(self):
        if not self.conn:
            raise RuntimeError("Database not connected")
        await self.conn.commit()

    async def rollback(self):
        if not self.conn:
            raise RuntimeError("Database not connected")
        await self.conn.rollback()

    async def fetchone(self, query: str, params: tuple = ()):
        if not self.conn:
            raise RuntimeError("Database not connected")
        async with self.conn.execute(query, params) as cursor:
            return await cursor.fetchone()

    async def fetchall(self, query: str, params: tuple = ()):
        if not self.conn:
            raise RuntimeError("Database not connected")
        async with self.conn.execute(query, params) as cursor:
            return await cursor.fetchall()
