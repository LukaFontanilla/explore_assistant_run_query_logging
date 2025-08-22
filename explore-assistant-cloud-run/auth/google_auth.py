import logging
import time

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

# Cache for the auth token
CACHED_TOKEN = None
TOKEN_EXPIRATION_TIME = 0

async def get_auth_token():
    """
    Gets a Google Auth token, caching it to improve performance.
    """
    global CACHED_TOKEN, TOKEN_EXPIRATION_TIME

    now = time.time()
    if CACHED_TOKEN and now < TOKEN_EXPIRATION_TIME:
        return CACHED_TOKEN

    try:
        from google.auth import default
        from google.auth.transport.requests import Request as gRequest
        credentials, _ = default(scopes=SCOPES)
        auth_req = gRequest()
        credentials.refresh(auth_req)
        if credentials.valid:
            CACHED_TOKEN = credentials.token
            # Tokens are typically valid for 1 hour, so we'll refresh after 55 minutes
            TOKEN_EXPIRATION_TIME = now + 3300
            return CACHED_TOKEN
    except Exception as e:
        logging.error(f"Error getting Google Auth token: {e}")
        return None
