import os

TOKEN = os.environ.get("TEST_TOKEN", "7474496771:AAGsJjBLGWhg4s69kS54_S7RXbdqSBO5Lrk")

SECRET_KEY = os.environ.get("SECRET_KEY", "1")
KUMA_TOKEN = os.environ.get("KUMA_TOKEN", "")
ADMINS = [2138964363, 348596474]
MERCHANT_ACCOUNT = os.environ.get("MERCHANT_ACCOUNT", "t_me_48799")
MERCHANT_DOMAIN_NAME = os.environ.get(
    "MERCHANT_DOMAIN_NAME", "https://t.me/info_realtor_bot"
)
SENTRY_SDK = os.environ.get("SENTRY_SDK", "")
