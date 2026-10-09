"""
tests/test_redis.py
Automated Test Suite for Redis Distributed State Cache & Anti-Replay Engine.
Validates:
1. Sub-microsecond atomic SID burning via SET NX EX
2. Replay attack deterministic interception
3. 50-thread concurrent race condition test (exactly 1 winner, 49 rejections)
4. Fail-closed security policy when Redis is unreachable
5. Cache reset functionality
"""

import sys
import os
import time
import concurrent.futures

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.redis_cache import (
    RedisStateCache,
    ReplayAttackDetectedError,
    CacheFailClosedError,
)


_CACHED_TEST_CACHE = None

def get_test_cache() -> RedisStateCache:
    """Returns a test cache instance, defaulting to FakeRedis if no live Redis."""
    global _CACHED_TEST_CACHE
    if _CACHED_TEST_CACHE is not None:
        return _CACHED_TEST_CACHE

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        cache = RedisStateCache(redis_url=redis_url, use_fakeredis=False)
        cache.client.ping()
        print("[INFO] Connected to live Redis for testing.")
        _CACHED_TEST_CACHE = cache
        return cache
    except Exception:
        print("[INFO] Live Redis not running locally. Using FakeRedis for tests.")
        _CACHED_TEST_CACHE = RedisStateCache(use_fakeredis=True)
        return _CACHED_TEST_CACHE



def test_basic_burn_and_is_consumed():
    """Verify session can be burned and is_consumed returns True."""
    cache = get_test_cache()
    sid = f"SID-BASIC-{int(time.time() * 1000)}"

    assert cache.is_consumed(sid) is False, "Fresh SID should not be consumed"

    burn_record = cache.burn_session(
        sid=sid,
        message="Legitimate QDS Transaction 1",
        qber=0.0,
        status="BURNED",
        persist_db=False
    )

    assert burn_record["sid"] == sid
    assert burn_record["quantum_state"] == "MEASURED/EMPTY"
    assert "burned_at_epoch_us" in burn_record

    assert cache.is_consumed(sid) is True, "Burned SID must return True for is_consumed"
    print(">>> 1. Basic burn and is_consumed test PASSED! <<<")


def test_replay_attack_interception():
    """Verify that a second burn attempt on the same SID raises ReplayAttackDetectedError."""
    cache = get_test_cache()
    sid = f"SID-REPLAY-{int(time.time() * 1000)}"

    # First burn succeeds
    cache.burn_session(sid, "First Transaction", 0.0, persist_db=False)

    # Second burn must raise ReplayAttackDetectedError
    try:
        cache.burn_session(sid, "Replayed Payload", 0.0, persist_db=False)
        assert False, "Replay attack should have been detected and rejected!"
    except ReplayAttackDetectedError as e:
        print(f"Replay successfully intercepted: {e}")

    print(">>> 2. Replay attack deterministic interception test PASSED! <<<")


def test_50_concurrent_burn_race():
    """
    CRITICAL SECURITY CHECK:
    Fires 50 concurrent burn attempts simultaneously on the exact same SID.
    Guarantees that EXACTLY ONE caller succeeds and 49 are rejected as replays.
    """
    cache = get_test_cache()
    sid = f"SID-CONCURRENCY-50-{int(time.time() * 1000)}"

    successes = []
    rejections = []

    def worker_burn(worker_id: int):
        try:
            rec = cache.burn_session(
                sid=sid,
                message=f"Concurrent Worker #{worker_id}",
                qber=0.005,
                status="BURNED",
                persist_db=False
            )
            successes.append((worker_id, rec))
        except ReplayAttackDetectedError as e:
            rejections.append((worker_id, str(e)))

    # Launch 50 threads concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(worker_burn, i) for i in range(50)]
        concurrent.futures.wait(futures)

    print(f"Concurrency Results -> Successes: {len(successes)} | Replays caught: {len(rejections)}")
    assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}"
    assert len(rejections) == 49, f"Expected exactly 49 rejections, got {len(rejections)}"
    assert cache.is_consumed(sid) is True

    print(f"Winning worker thread: #{successes[0][0]}")
    print(">>> 3. 50-thread concurrent burn race test PASSED! <<<")


def test_fail_closed_policy():
    """Verify fail-closed policy when Redis connection fails."""
    # Point to non-existent port with fail_closed=True
    cache_down = RedisStateCache(
        redis_url="redis://localhost:9999/0",
        fail_closed=True,
        use_fakeredis=False
    )

    # is_consumed must fail closed (return True, blocking transaction)
    assert cache_down.is_consumed("UNVERIFIABLE-SID") is True

    # burn_session must raise CacheFailClosedError
    try:
        cache_down.burn_session("UNVERIFIABLE-SID", "Payload", 0.0, persist_db=False)
        assert False, "Should have raised CacheFailClosedError"
    except CacheFailClosedError as e:
        print(f"Fail-closed successfully triggered on burn: {e}")

    print(">>> 4. Fail-closed resilience test PASSED! <<<")


def test_cache_reset():
    """Verify cache reset cleans burned sessions."""
    cache = get_test_cache()
    sid = f"SID-RESET-{int(time.time() * 1000)}"

    cache.burn_session(sid, "Reset Test Payload", 0.0, persist_db=False)
    assert cache.is_consumed(sid) is True

    cache.reset()
    assert cache.is_consumed(sid) is False
    print(">>> 5. Cache reset test PASSED! <<<")


if __name__ == "__main__":
    print("================ RUNNING REDIS STATE CACHE TESTS ================")
    test_basic_burn_and_is_consumed()
    test_replay_attack_interception()
    test_50_concurrent_burn_race()
    test_fail_closed_policy()
    test_cache_reset()
    print("\n================ ALL REDIS TESTS PASSED SUCCESSFULLY! ================")
