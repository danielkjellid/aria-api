import pytest
from aria.core.decorators import not_in_production, NotAllowedInProductionException


class TestCoreDecorator:
    def test_not_in_production_decorator(self, settings):

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
