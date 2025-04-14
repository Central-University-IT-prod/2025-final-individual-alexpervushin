import uuid
from datetime import datetime
from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ForbiddenWordsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[str]:
        result = await self.session.execute(
            text("SELECT word FROM forbidden_words ORDER BY word")
        )
        return [row[0] for row in result.fetchall()]

    async def update(self, data: List[str]) -> None:
        current_time = datetime.now()

        await self.session.execute(text("DELETE FROM forbidden_words"))

        for word in data:
            await self.session.execute(
                text("""
                    INSERT INTO forbidden_words (id, word, created_at, updated_at)
                    VALUES (:id, :word, :created_at, :updated_at)
                """),
                {
                    "id": uuid.uuid4(),
                    "word": word,
                    "created_at": current_time,
                    "updated_at": current_time,
                },
            )

        await self.session.flush()
