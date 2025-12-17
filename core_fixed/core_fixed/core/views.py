import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests

from hypertension.models import GoogleFitToken


@login_required
def googlefit_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("No code returned from Google.")

    # Exchange authorization code for token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data).json()

    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    token_type = response.get("token_type", "Bearer")
    scope = response.get("scope", "")

    if not access_token:
        return HttpResponse(f"Token error: {response}")

    # Calculate expiry datetime
    expiry_time = timezone.now() + datetime.timedelta(seconds=expires_in)

    # Save or update token for current user
    GoogleFitToken.objects.update_or_create(
        user=request.user,
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token_type,
            "expires_in": expires_in,
            "expires_at": expiry_time,
            "scope": scope,
        }
    )

    return HttpResponse("Google Fit connected ✔ Tokens saved successfully!")
