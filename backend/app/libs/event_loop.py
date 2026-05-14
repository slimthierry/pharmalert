"""
Shared event loop policy for asyncpg SQLAlchemy engine.

This must be initialized at application startup and used consistently
across all asyncpg connections to avoid the error:
    "RuntimeError: Task got Future attached to a different loop"

Usage:
    In app.main:
        from app.libs.event_loop import init_event_loop
        init_event_loop()

    In database.py (engine creation):
        from app.libs.event_loop import get_asyncpg_connection_kwargs
        create_async_engine(..., loop_pool=True)

    In middleware that creates its own sessions:
        from app.libs.event_loop import run_in_executor_loop
        run_in_executor_loop(async_log_function)
"""

import asyncio
import threading
import weakref
from typing import Callable, Awaitable

# Global event loop policy
_loop_policy: asyncio.AbstractEventLoopPolicy | None = None
_loop_lock = threading.Lock()


class SingleThreadEventLoopPolicy(asyncio.AbstractEventLoopPolicy):
    """
    An event loop policy that ensures all asyncpg connections use the same loop.

    This prevents "attached to a different loop" errors by keeping all loops
    in a single background thread and routing all tasks to that thread.
    """

    def __init__(self):
        super().__init__()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._loop_holder = None  # weakref to avoid circular reference

    def _get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None or self._loop.is_closed():
            with _loop_lock:
                if self._loop is None or self._loop.is_closed():
                    q = asyncio.Queue()
                    stopped = False

                    def runner():
                        nonlocal stopped
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        self._loop = loop
                        # Keep a weak reference to avoid GC issues
                        self._loop_holder = weakref.ref(loop)
                        q.put(loop)
                        loop.run_forever()
                        while not stopped:
                            loop.run_until_complete(asyncio.sleep(0.1))
                        loop.close()

                    self._thread = threading.Thread(target=runner, daemon=True)
                    self._thread.start()
                    # Wait for the loop to be ready
                    self._loop = q.get(timeout=5)
        return self._loop

    def get_child_loop(self) -> asyncio.AbstractEventLoop:
        """Override to always return the shared loop."""
        return self._get_or_create_loop()

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        """Override to always return the shared loop."""
        return self._get_or_create_loop()

    def set_event_loop(self, loop: asyncio.AbstractEventLoop | None) -> None:
        # Silently ignore — we control the loop
        pass

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Override to always return the shared loop."""
        if self._loop is None or self._loop.is_closed():
            return self._get_or_create_loop()
        return self._loop

    def close(self) -> None:
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)


_policy_instance: SingleThreadEventLoopPolicy | None = None


def init_event_loop() -> None:
    """
    Initialize the shared event loop policy.

    Call this at application startup (e.g., in app.main lifespan).
    """
    global _policy_instance
    if _policy_instance is None:
        _policy_instance = SingleThreadEventLoopPolicy()
        asyncio.set_event_loop_policy(_policy_instance)


def run_in_shared_loop(coro: Awaitable) -> asyncio.Future:
    """
    Schedule a coroutine to run in the shared event loop from any thread.

    Returns a Future that can be awaited for the result.
    """
    policy = _policy_instance or SingleThreadEventLoopPolicy()
    loop = policy.get_event_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop)


def run_sync_in_shared_loop(func: Callable) -> asyncio.Future:
    """
    Run a synchronous function inside the shared event loop.

    Returns a Future that resolves when the function completes.
    """
    async def _wrapper():
        return func()

    policy = _policy_instance or SingleThreadEventLoopPolicy()
    loop = policy.get_event_loop()
    return asyncio.run_coroutine_threadsafe(_wrapper(), loop)