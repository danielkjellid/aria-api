from dataclasses import dataclass

from django.core.cache import cache

import pytest

from aria.core.decorators import (
    NotAllowedInProductionException,
    cached,
    not_in_production,
)


class TestCoreDecorators:
    def test_not_in_production_decorator(self, settings) -> None:

        settings.PRODUCTION = False
        settings.ENVIRONMENT = "dev"

        @not_in_production
        def func_a() -> int:
            return 1 + 1

        assert func_a() == 2

        # Test production true, but environment not equal to production
        # makes exception raise.
        settings.PRODUCTION = True
        settings.ENVIRONMENT = "dev"

        with pytest.raises(NotAllowedInProductionException):
            func_a()

        # Test production false, but environment equal to production
        # makes exception raise.
        settings.PRODUCTION = False
        settings.ENVIRONMENT = "production"

        with pytest.raises(NotAllowedInProductionException):
            func_a()

        # Test both production true and environment equal to production
        # makes exception raise.
        settings.PRODUCTION = True
        settings.ENVIRONMENT = "production"

        with pytest.raises(NotAllowedInProductionException):
            func_a()

    def test_cached_decorator(self) -> None:
        @dataclass(frozen=True, eq=True)
        class MyDataClass:
            id: int
            a_list: list[int]

        @cached(key="func_a")
        def func_a() -> MyDataClass:
            func_a.num_times_called += 1
            return MyDataClass(id=func_a.num_times_called, a_list=[1, 2])

        @cached(key="func_b")
        def func_b() -> list[MyDataClass]:
            func_b.num_times_called += 1
            return [MyDataClass(id=func_a.num_times_called, a_list=[1, 2])]

        func_a.num_times_called = 0
        func_b.num_times_called = 0

        assert "func_a" not in cache
        assert func_a() == MyDataClass(id=1, a_list=[1, 2])
        assert cache.get("func_a") == {"id": 1, "a_list": [1, 2]}
        assert func_a() == MyDataClass(id=1, a_list=[1, 2])
        assert func_a.num_times_called == 1

        assert "func_b" not in cache
        assert func_b() == [MyDataClass(id=1, a_list=[1, 2])]
        assert cache.get("func_b") == [{"id": 1, "a_list": [1, 2]}]
        assert func_b() == [MyDataClass(id=1, a_list=[1, 2])]
        assert func_b.num_times_called == 1

        func_b.uncache()
        assert "func-b" not in cache
