import os

TOKEN = os.environ["TEST_TOKEN"]
SECRET_KEY = os.environ["SECRET_KEY"]
ADMINS = [2138964363, 348596474]
MERCHANT_ACCOUNT = os.environ.get("MERCHANT_ACCOUNT", "t_me_48799")
MERCHANT_DOMAIN_NAME = os.environ.get(
    "MERCHANT_DOMAIN_NAME", "https://t.me/info_realtor_bot"
)
