from ninja import NinjaAPI
from aria.users.viewsets.public import public_endpoint as public_users_enpoints

api = NinjaAPI()

api.add_router('/users/', public_users_enpoints)