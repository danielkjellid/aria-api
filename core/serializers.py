from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = 'username'
        
    default_error_messages = {
        'no_active_account': 'Feil brukernavn eller passord. Merk at du må skille mellom store og små bokstaver.'
    }