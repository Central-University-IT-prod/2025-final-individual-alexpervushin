import asyncio
import logging
from types import TracebackType
from typing import Awaitable, Callable, Protocol, TypeVar

from sqlalchemy.exc import OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import click_lock, impression_lock
from typing_extensions import Self

T = TypeVar("T", bound="AbstractUow")
R = TypeVar("R")

logger = logging.getLogger(__name__)


class AbstractUow(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    @property
    def click_lock(self) -> asyncio.Lock: ...

    @property
    def impression_lock(self) -> asyncio.Lock: ...

    @property
    def session(self) -> AsyncSession: ...


class SQLAlchemyUow(AbstractUow):
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._retries = 0

    @property
    def click_lock(self) -> asyncio.Lock:
        return click_lock

    @property
    def impression_lock(self) -> asyncio.Lock:
        return impression_lock

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                logger.error(
                    f"Error in uow: {exc_value}, exc_type: {exc_type}, traceback: {traceback}",
                )
                await self.rollback()
        finally:
            await self._session.close()

    async def _execute_with_retry(self, operation: Callable[[], Awaitable[R]]) -> R:
        while True:
            try:
                return await operation()
            except (TimeoutError, OperationalError) as e:
                self._retries += 1
                if self._retries >= self.MAX_RETRIES:
                    logger.error(
                        f"Max retries ({self.MAX_RETRIES}) reached. Error: {str(e)}"
                    )
                    raise

                wait_time = self.RETRY_DELAY * (2 ** (self._retries - 1))
                logger.warning(
                    f"Db operation failed. Retrying in {wait_time} seconds. Error: {str(e)}"
                )
                await asyncio.sleep(wait_time)
                continue

    async def commit(self) -> None:
        try:
            await self._execute_with_retry(self._session.commit)
        except Exception as e:
            logger.error(f"Error during commit: {str(e)}")
            await self.rollback()
            raise

    async def rollback(self) -> None:
        try:
            await self._session.rollback()
        except Exception as e:
            logger.error(f"Error during rollback: {str(e)}")
            raise

    @property
    def session(self) -> AsyncSession:
        return self._session
