# core/hypertension/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpRequest
from django.apps import apps
import json
from typing import Optional

# Local imports
from .models import BloodPressureReading
from .forms import BPReadingForm  # ensure this form exists and maps to the model
from hypertension.utils import classify_bp  # elder-friendly classifier


# -----------------------
# Helper: get Profile safely
# -----------------------
def _get_profile_model():
    """
    Lazily resolve the Profile model so imports don't break during startup.
    """
    try:
        return apps.get_model("hypertension", "Profile")
    except LookupError:
        return None


# -----------------------
# Signup views
# -----------------------
def signup_test(request: HttpRequest):
    """Simple test view to ensure routing works."""
    return HttpResponse("<h1>SIGNUP VIEW WORKS</h1>")


def signup_view(request: HttpRequest):
    """
    Signup view using Django's UserCreationForm.
    On successful signup the user is created, profile ensured, logged in and redirected.
    """
    next_url = request.GET.get("next") or request.POST.get("next") or None

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure a Profile exists for the new user (signals will also run if present)
            Profile = _get_profile_model()
            if Profile is not None:
                Profile.objects.get_or_create(user=user)

            # Automatically log the user in after signup
            login(request, user)
            messages.success(request, "Account created and logged in.")
            # Redirect to the bp list (namespaced)
            if next_url:
                return redirect(next_url)
            return redirect("hypertension:bp_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form, "next": next_url})


# -----------------------
# Small BP classifier (fallback if you want to use here)
# -----------------------
def _classify_bp_label(systolic: int, diastolic: int) -> str:
    """
    Return a short label (fallback) — primarily we use hypertension.utils.classify_bp elsewhere.
    """
    try:
        s = int(systolic)
        d = int(diastolic)
    except Exception:
        return "Unclassified"

    if s < 120 and d < 80:
        return "Normal"
    if 120 <= s < 130 and d < 80:
        return "Elevated"
    if (130 <= s < 140) or (80 <= d < 90):
        return "Stage 1"
    if s >= 140 or d >= 90:
        return "Stage 2"
    return "Unclassified"


# -----------------------
# Dashboard
# -----------------------
@login_required
def dashboard_view(request: HttpRequest):
    """
    Main dashboard view showing a quick BP card, chart data, and recent readings.
    Passes:
      - latest
      - stage (label, badge) or None
      - advice (string) or None
      - readings (queryset)
      - labels_json, systolic_json, diastolic_json for charts (if needed)
    """
    Profile = _get_profile_model()
    if Profile is None:
        # If profile model isn't available yet, render a simplified dashboard
        return render(request, "dashboard.html", {"user": request.user})

    profile, _ = Profile.objects.get_or_create(user=request.user)

    # latest 50 readings (most recent first)
    readings_qs = BloodPressureReading.objects.filter(profile=profile).order_by("-recorded_at")[:50]
    latest = readings_qs.first()

    # classification & advice using hypertension.utils.classify_bp if available
    stage = None
    advice = None
    if latest:
        try:
            label, badge, advice_text, severity = classify_bp(latest.systolic, latest.diastolic)
            stage = (label, badge)
            advice = advice_text
        except Exception:
            # fallback to simple label
            stage = (_classify_bp_label(latest.systolic, latest.diastolic), "secondary")
            advice = None

    # prepare chart data (chronological)
    chart_qs = list(readings_qs.order_by("recorded_at")[:50])
    times = [r.recorded_at.strftime("%Y-%m-%d %H:%M") for r in chart_qs]
    syst = [r.systolic for r in chart_qs]
    dias = [r.diastolic for r in chart_qs]

    context = {
        "readings": readings_qs,
        "latest": latest,
        "stage": stage,
        "advice": advice,
        "labels_json": json.dumps(times),
        "systolic_json": json.dumps(syst),
        "diastolic_json": json.dumps(dias),
    }
    return render(request, "hypertension/dashboard.html", context)


# -----------------------
# BP CRUD Views
# -----------------------
@login_required
def bp_list(request: HttpRequest):
    """
    Show the latest blood pressure readings for the logged-in user's profile.
    Supplies JSON arrays for charting (labels_json, systolic_json, diastolic_json).
    """
    Profile = _get_profile_model()
    profile, _ = (Profile.objects.get_or_create(user=request.user) if Profile else (None, None))

    if profile is None:
        readings_qs = BloodPressureReading.objects.none()
    else:
        readings_qs = BloodPressureReading.objects.filter(profile=profile).order_by("-recorded_at")[:50]

    readings = list(readings_qs)  # convert to list so we can reverse for chronological chart
    readings_chrono = readings[::-1]  # old -> new
    labels = [r.recorded_at.strftime("%Y-%m-%d %H:%M") for r in readings_chrono]
    systolic = [r.systolic for r in readings_chrono]
    diastolic = [r.diastolic for r in readings_chrono]

    context = {
        "readings": readings_qs,
        "labels_json": json.dumps(labels),
        "systolic_json": json.dumps(systolic),
        "diastolic_json": json.dumps(diastolic),
    }

    # debug helper
    print("DEBUG bp_list: n_readings=", len(readings), "labels_len=", len(labels))
    return render(request, "hypertension/bp_list.html", context)


@login_required
def bp_create(request: HttpRequest):
    """
    Create a new BP reading for the logged-in user's profile.
    GET -> show form, POST -> validate and save.
    """
    Profile = _get_profile_model()
    profile, _ = (Profile.objects.get_or_create(user=request.user) if Profile else (None, None))

    if request.method == "POST":
        form = BPReadingForm(request.POST)
        if form.is_valid():
            bp = form.save(commit=False)
            # attach to profile if available
            if profile:
                bp.profile = profile
            if not getattr(bp, "recorded_at", None):
                bp.recorded_at = timezone.now()
            bp.save()
            messages.success(request, "New reading saved.")
            return redirect("hypertension:bp_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BPReadingForm()

    return render(request, "hypertension/bp_form.html", {"form": form})


@login_required
def bp_edit(request: HttpRequest, pk: int):
    """
    Edit an existing BP reading. Only allows editing if the reading belongs to the user's profile.
    """
    Profile = _get_profile_model()
    profile, _ = (Profile.objects.get_or_create(user=request.user) if Profile else (None, None))

    bp = get_object_or_404(BloodPressureReading, pk=pk, profile=profile)

    if request.method == "POST":
        form = BPReadingForm(request.POST, instance=bp)
        if form.is_valid():
            form.save()
            messages.success(request, "Reading updated.")
            return redirect("hypertension:bp_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BPReadingForm(instance=bp)
    return render(request, "hypertension/bp_form.html", {"form": form, "bp": bp})


@login_required
def bp_delete(request: HttpRequest, pk: int):
    """
    Confirm and delete a BP reading. Only allow delete if reading belongs to the user's profile.
    """
    Profile = _get_profile_model()
    profile, _ = (Profile.objects.get_or_create(user=request.user) if Profile else (None, None))

    bp = get_object_or_404(BloodPressureReading, pk=pk, profile=profile)

    if request.method == "POST":
        bp.delete()
        messages.success(request, "Reading deleted.")
        return redirect("hypertension:bp_list")
    return render(request, "hypertension/bp_confirm_delete.html", {"bp": bp})


# -----------------------
# Quick Access Placeholder Views (under hypertension app)
# -----------------------
@login_required
def bp_home(request: HttpRequest):
    """
    Placeholder page for the BP tile (under the hypertension app).
    Can be extended to reuse readings/labels_json for inline charts.
    """
    # optional: pass readings/labels_json like in bp_list
    return render(request, "sections/bp_home.html")


@login_required
def medications_home(request: HttpRequest):
    """
    Placeholder page for Medications tile.
    """
    return render(request, "sections/medications_home.html")


@login_required
def salt_home(request: HttpRequest):
    """
    Placeholder page for Salt Intake tile.
    """
    return render(request, "sections/salt_home.html")


@login_required
def food_home(request: HttpRequest):
    """
    Placeholder page for My Food Today tile.
    """
    return render(request, "sections/food_home.html")


@login_required
def devices_home(request: HttpRequest):
    """
    Placeholder page for Spoon & Watch (devices) tile.
    """
    return render(request, "sections/devices_home.html")


@login_required
def reminders_home(request: HttpRequest):
    """
    Placeholder page for Reminders tile.
    """
    return render(request, "sections/reminders_home.html")
