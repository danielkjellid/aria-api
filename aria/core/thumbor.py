from django.conf import settings

from libthumbor import CryptoURL

crypto_url = CryptoURL(key=settings.THUMBOR_SECURITY_KEY)


def generate_signed_url(image_name: str, width: int, height: int) -> str:
    """
    Generate a signed
    """

    thumbor_server_url = settings.THUMBOR_SERVER_URL.rstrip("/")
    signed_url = crypto_url.generate(
        image_url=image_name, width=width, height=height, smart=True
    ).strip("/")

    return f"{thumbor_server_url}/{signed_url}"
