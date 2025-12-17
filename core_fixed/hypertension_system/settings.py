# ===============================
# GOOGLE FIT API SETTINGS
# ===============================
import os

GOOGLE_FIT_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_FIT_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_FIT_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/googlefit/callback/")

GOOGLE_FIT_SCOPES = (
    "https://www.googleapis.com/auth/fitness.heart_rate.read "
    "https://www.googleapis.com/auth/fitness.activity.read "
    "https://www.googleapis.com/auth/fitness.sleep.read "
    "https://www.googleapis.com/auth/fitness.body.read "
)
