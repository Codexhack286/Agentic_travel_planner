def get_rate_limiter(*args, **kwargs):
    class MockRateLimiter:
        async def acquire(self):
            pass
    return MockRateLimiter()
