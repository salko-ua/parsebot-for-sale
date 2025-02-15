import os

#TOKEN = os.environ["TEST_TOKEN"]
TOKEN = "7474496771:AAGsJjBLGWhg4s69kS54_S7RXbdqSBO5Lrk"
SECRET_KEY = os.environ["SECRET_KEY"]
KUMA_TOKEN = os.environ.get("KUMA_TOKEN", "")
ADMINS = [2138964363, 348596474]
MERCHANT_ACCOUNT = os.environ.get("MERCHANT_ACCOUNT", "t_me_48799")
MERCHANT_DOMAIN_NAME = os.environ.get("MERCHANT_DOMAIN_NAME", "https://t.me/info_realtor_bot")
SENTRY_SDK = os.environ.get("SENTRY_SDK", "")
