import pyotp
from SmartApi import SmartConnect
from config import apikey, username, pwd, token
from logzero import logger

def login_and_setup():
    """
    Initializes SmartConnect, authenticates using TOTP credentials from config.py,
    performs generateSession, renews access tokens, and returns the active smartApi object.
    """
    smartApi = SmartConnect(api_key=apikey)
    
    try:
        totp = pyotp.TOTP(token).now()
    except Exception as e:
        logger.error(f"Failed to generate TOTP: {e}")
        raise e

    logger.info("Connecting to SmartAPI and generating login session...")
    login_data = smartApi.generateSession(username, pwd, totp)
    
    if not login_data.get('status'):
        logger.error(f"Login failed: {login_data.get('message', 'Unknown Error')}")
        raise Exception(f"Authentication failed: {login_data.get('message')}")
        
    refreshToken = login_data['data']['refreshToken']
    
    # Renew token to ensure a fresh, active access token for all secure REST operations
    logger.info("Renewing access tokens...")
    smartApi.generateToken(refreshToken)
    
    logger.info("Authentication setup completed successfully.")
    return smartApi
