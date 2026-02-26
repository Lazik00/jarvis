import logging
from pathlib import Path
from typing import Any

import aiosqlite

logger = logging.getLogger("jarvis.memory")


class MemoryStore:
    def __init__(self, db_path: str = "data/jarvis.db", use_vector: bool = False) -> None:
        self.db_path = Path(db_path)
        self.conn: aiosqlite.Connection | None = None
        self.use_vector = use_vector
        self.vector_collection = None

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await self.conn.commit()

        if self.use_vector:
            try:
                import chromadb

                client = chromadb.PersistentClient(path="data/chroma")
                self.vector_collection = client.get_or_create_collection("jarvis_memory")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Vector memory disabled: %s", exc)

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    async def save_message(self, role: str, content: str) -> None:
        if not self.conn:
            return
        await self.conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
        await self.conn.commit()

        if self.vector_collection:
            try:
                msg_id = f"{role}-{abs(hash(content))}"
                self.vector_collection.upsert(ids=[msg_id], documents=[content], metadatas=[{"role": role}])
            except Exception as exc:  # noqa: BLE001
                logger.warning("Vector save failed: %s", exc)

    async def recent_messages(self, limit: int = 10) -> list[dict[str, str]]:
        if not self.conn:
            return []
        cursor = await self.conn.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [{"role": role, "content": content} for role, content in reversed(rows)]

    async def search_memory(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if self.vector_collection:
            try:
                result = self.vector_collection.query(query_texts=[query], n_results=limit)
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                return [{"content": d, "meta": m} for d, m in zip(docs, metas)]
            except Exception as exc:  # noqa: BLE001
                logger.warning("Vector search failed: %s", exc)

        if not self.conn:
            return []
        like_query = f"%{query}%"
        cursor = await self.conn.execute(
            "SELECT role, content, created_at FROM messages WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (like_query, limit),
        )
        rows = await cursor.fetchall()
        return [
            {"role": role, "content": content, "created_at": created_at}
            for role, content, created_at in rows
        ]
