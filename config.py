import os

# API Credentials 
apikey = os.getenv("ANGEL_API_KEY", "")
username = os.getenv("ANGEL_USERNAME", "")
pwd = os.getenv("ANGEL_PASSWORD", "")
token = os.getenv("ANGEL_TOTP_SECRET", "")

