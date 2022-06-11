import functools
import inspect
import logging
from typing import Any, Callable, Optional, TypeVar, cast

from django.conf import settings
from django.core.cache import cache

from aria.core.cache_utils import get_codec

F = TypeVar("F", bound=Callable[..., Any])
logger = logging.getLogger(__name__)


class NotAllowedInProductionException(Exception):
    pass


def not_in_production(func: Any) -> Callable[[F], F]:
    """
    Decorator that raises exception if run in production.
    Typically used for management commands that changes production data.
    """

    def inner(*args: Any, **kwargs: Any) -> Any:
        if settings.PRODUCTION or settings.ENVIRONMENT == "production":
            raise NotAllowedInProductionException(
                "This operation is not allowed in production!"
            )

        return func(*args, **kwargs)

    return inner


def cached(
    *, key: str | Callable[..., str], timeout: Optional[int] = 60
) -> Callable[[F], F]:
    """
    Caches the result of a method using a key, being a string or function,
    for an amount of seconds.

    E.g:      @cached(key="my-key", timeout=(60 * 60))
    or:       @cached(key=lambda instance: f"my-key.{instance.id}", timeout=(60 * 60))

    NOTE: The lambda/key function must accept exactly the same arguments (*args and **kwargs)
    as the decorated function with same arguments are passed to the key function.

    This supports safely caching dataclasses, but only if the return value of the
    decorated function is properly typed. Eg.:

        @cached(key=lambda arg: f"my-key.{arg}")
        def my_function(*, arg: str) -> MyDataclass:
            ...

    This also provides a helper to clear the cache. This must be provided with
    the same arguments as the function.

    E.g:    my_function.uncache(arg="hello")
    """

    get_cache_key: Callable[..., str]

    if isinstance(key, str) and key:
        get_cache_key = lambda *args, **kwargs: cast(str, key)  # noqa
    elif callable(key):
        get_cache_key = key
    else:
        raise TypeError(f"Key must be a non-empty string or callable: {key}")

    def uncache(*args: Any, **kwargs: Any) -> Any:
        """
        Helper to clear the cache. Takes the same arguments as the function.
        """

        cache_key = get_cache_key(*args, **kwargs)
        cache.delete(cache_key)

    def decorator(func: F) -> F:
        signature = inspect.signature(func)
        encoder, decoder = get_codec(type_annotation=signature.return_annotation)

        @functools.wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            """
            Returns the new function, wrapping fn and only calling it if no
            value was found in the cache.
            """

            cache_key = get_cache_key(*args, **kwargs)

            try:
                cached_value = cache.get(cache_key)
            except Exception as exc:
                logger.error(f"Cache read failed for key {cache_key}", exc_info=exc)
                cached_value = None

            if cached_value is not None:
                value = decoder(cached_value)
            else:
                # Value is not in cache, so calculate and update cache
                value = func(*args, **kwargs)
                value_for_cache = encoder(value)

                try:
                    cache.set(cache_key, value_for_cache, timeout=timeout)
                except Exception as exc:
                    logger.error(
                        f"Cache write failed for key: {cache_key}", exc_info=exc
                    )

            return value

        # Add the uncache helper as a attribute of the function
        inner.uncache = uncache  # type: ignore

        return cast(F, inner)

    return decorator
