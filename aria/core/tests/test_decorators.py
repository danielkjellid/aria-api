from dataclasses import dataclass
from typing import Any

from django.core.cache import cache

import pytest
from pydantic import BaseModel

from aria.core.decorators import (
    NotAllowedInProductionException,
    cached,
    not_in_production,
)


class TestCoreDecorators:
    def test_not_in_production_decorator(self, settings) -> None:
        """
        Test that the @not_in_production decorator throws an
        exception if decorated function is used in production.
        """
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
        """
        Test that the @cached decorator caches content.
        """

        # Test normal object (dict).
        # @cached(key="func_a")
        # def func_a() -> dict[str, Any]:
        #     func_a.num_times_called += 1
        #     return {"id": func_a.num_times_called, "a_list": [1, 2]}
        #
        # func_a.num_times_called = 0
        #
        # assert "func_a" not in cache
        # assert func_a() == {"id": 1, "a_list": [1, 2]}
        # assert "func_a" in cache
        # assert cache.get("func_a") == {"id": 1, "a_list": [1, 2]}
        # assert func_a.num_times_called == 1
        #
        # func_a.uncache()
        # assert "func_a" not in cache
        #
        # # Test normal objects (list of dicts).
        # @cached(key="func_b")
        # def func_b() -> list[dict[str, Any]]:
        #     func_b.num_times_called += 1
        #     return [{"id": func_b.num_times_called, "a_list": [1, 2]}]
        #
        # func_b.num_times_called = 0
        #
        # assert "func_b" not in cache
        # assert func_b() == [{"id": 1, "a_list": [1, 2]}]
        # assert "func_b" in cache
        # assert cache.get("func_b") == [{"id": 1, "a_list": [1, 2]}]
        # assert func_b.num_times_called == 1
        #
        # func_b.uncache()
        # assert "func_b" not in cache

        class MyPydanticModel(BaseModel):
            id: int
            a_list: list[int]

        # Test pydantic model.
        # @cached(key="func_c")
        # def func_c() -> BaseModel:
        #     func_c.num_times_called += 1
        #     return MyPydanticModel(id=func_c.num_times_called, a_list=[1, 2])
        #
        # func_c.num_times_called = 0
        #
        # assert "func_c" not in cache
        # assert func_c() == MyPydanticModel(id=func_c.num_times_called, a_list=[1, 2])
        # assert "func_c" in cache
        # assert cache.get("func_c") == {"id": 1, "a_list": [1, 2]}
        # assert func_c.num_times_called == 1
        #
        # func_c.uncache()
        # assert "func_c" not in cache

        # Test list of pydantic models.
        @cached(key="func_d")
        def func_d() -> list[BaseModel]:
            func_d.num_times_called += 1
            return [MyPydanticModel(id=func_d.num_times_called, a_list=[1, 2])]

        func_d.num_times_called = 0

        assert "func_d" not in cache
        assert func_d() == [MyPydanticModel(id=func_d.num_times_called, a_list=[1, 2])]
        assert "func_d" in cache
        assert cache.get("func_d") == [{"id": 1, "a_list": [1, 2]}]
        assert func_d.num_times_called == 1

        func_d.uncache()
        assert "func_d" not in cache
