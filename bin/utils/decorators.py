import os
import sys


def not_in_production(func):
    environment = os.environ.get("ENVIRONMENT")
    is_production = os.environ.get("PRODUCTION", True)

    def inner(*args, **kwargs):
        if environment == "production" or is_production is True:
            sys.exit("This command can not be run in production!")

        return func(*args, **kwargs)

    return inner


def not_in_dev(func):
    environment = os.environ.get("ENVIRONMENT")
    is_production = os.environ.get("PRODUCTION", False)

    def inner(*args, **kwargs):
        if environment != "production" or is_production is False:
            sys.exit("This command is a production script, and can not be run locally!")

        return func(*args, **kwargs)

    return inner
