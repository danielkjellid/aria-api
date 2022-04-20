from ninja import NinjaAPI
from aria.users.viewsets import public_endpoints as public_users_endpoints, internal_endpoints as internal_users_endpoints


endpoints = NinjaAPI()

endpoints.add_router('/users/', public_users_endpoints, tags=["public", "users [PUBLIC]"])
