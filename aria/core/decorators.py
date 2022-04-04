from django.conf import settings


class NotAllowedInProductionException(Exception):
    pass


def not_in_production(func):
    """
    Decorator that raises exception if run in production.
    Typically used for management commands that changes production data.
    """
    
    def inner(*args, **kwargs):
        if settings.PRODUCTION or settings.ENVIRONMENT == "prod":
            raise NotAllowedInProductionException("This operation is not allowed in production!")
        
        return func(*args, **kwargs)
    
    return inner
