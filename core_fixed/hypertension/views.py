# hypertension/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.apps import apps
import json

from .models import BloodPressureReading, WatchSync, WatchBloodPressure
from .forms import BPReadingForm


# ======================================================
#  HELPERS
# ======================================================

def _get_profile_model():
    """Safely load Profile model without circular import errors."""
    try:
        return apps.get_model("hypertension", "Profile")
    except LookupError:
        return None


# ======================================================
#  SIGNUP (uses UserCreationForm to match your template)
# ======================================================
def signup(request: HttpRequest):
    """
    Signup using Django's UserCreationForm and automatic login.
    Renders `accounts/signup.html` and passes a `form` context (matching the template).
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create Profile if model exists
            Profile = _get_profile_model()
            if Profile is not None:
                Profile.objects.get_or_create(user=user)

            # login the new user
            login(request, user)

            # prefer `next` if provided (GET or POST), otherwise go to dashboard
            next_url = request.POST.get('next') or request.GET.get('next') or "/dashboard/"
            return redirect(next_url)
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


# ======================================================
#  DASHBOARD
# ======================================================
@login_required
def dashboard_view(request: HttpRequest):

    Profile = _get_profile_model()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Query ordered descending (newest first) but don't slice yet if we
    # may need to reorder later for charts.
    readings_qs = BloodPressureReading.objects.filter(profile=profile).order_by("-recorded_at")

    # Take the latest 50 readings for display (descending)
    readings = readings_qs[:50]

    # latest reading for the card
    latest = readings.first()

    # charts (chronological ascending)
    # Re-order on the unsliced queryset, then slice to last 50 and convert to list
    chart_qs = readings_qs.order_by("recorded_at")[:50]
    chart = list(chart_qs)

    labels = [r.recorded_at.strftime("%Y-%m-%d %H:%M") for r in chart]
    systolic = [r.systolic for r in chart]
    diastolic = [r.diastolic for r in chart]

    # Classification helper (simple guideline)
    def classify_bp(s, d):
        if s is None or d is None:
            return None, None, None
        # Hypertensive crisis
        if s > 180 or d > 120:
            return "Hypertensive Crisis", "danger", "Seek emergency medical attention immediately."
        # Stage 2
        if s >= 140 or d >= 90:
            return "Stage 2 Hypertension", "danger", "This is high — contact your healthcare provider."
        # Stage 1
        if (130 <= s <= 139) or (80 <= d <= 89):
            return "Stage 1 Hypertension", "warning", "Lifestyle changes advised; consult your doctor."
        # Elevated
        if 120 <= s <= 129 and d < 80:
            return "Elevated", "info", "Elevated blood pressure — monitor and adopt healthy habits."
        # Normal
        if s < 120 and d < 80:
            return "Normal", "success", "Blood pressure is in the normal range. Keep it up!"
        return None, None, None

    stage = None
    advice = None
    if latest:
        label, color, msg = classify_bp(latest.systolic, latest.diastolic)
        if label:
            stage = (label, color)
            advice = msg

    try:
        watchsync = WatchSync.objects.get(user=request.user)
    except WatchSync.DoesNotExist:
        watchsync = None

    # latest watch reading (for dashboard critical area)
    latest_watch = WatchBloodPressure.objects.filter(watch_sync__user=request.user).order_by("-recorded_at").first()

    # classification for latest watch (for color alerts)
    watch_stage = None
    watch_advice = None
    if latest_watch:
        wlabel, wcolor, wmsg = classify_bp(latest_watch.systolic, latest_watch.diastolic)
        if wlabel:
            watch_stage = (wlabel, wcolor)
            watch_advice = wmsg

    return render(request, "hypertension/dashboard.html", {
        "readings": readings,
        "latest": latest,
        "labels_json": json.dumps(labels),
        "systolic_json": json.dumps(systolic),
        "diastolic_json": json.dumps(diastolic),
        "stage": stage,
        "advice": advice,
        "watchsync": watchsync,
        "latest_watch": latest_watch,
        "watch_stage": watch_stage,
        "watch_advice": watch_advice,
    })


# ======================================================
#  BP: LIST
# ======================================================

@login_required
def bp_list(request: HttpRequest):

    Profile = _get_profile_model()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # manual readings (chronological ascending)
    manual_qs = BloodPressureReading.objects.filter(profile=profile).order_by("recorded_at")

    # watch readings (chronological ascending)
    watch_qs = WatchBloodPressure.objects.filter(watch_sync__user=request.user).order_by("recorded_at")

    # Build combined chronological list (ascending)
    combined = []
    for r in manual_qs:
        combined.append({
            "source": "manual",
            "recorded_at": r.recorded_at,
            "systolic": r.systolic,
            "diastolic": r.diastolic,
            "pulse": getattr(r, 'pulse', None),
            "notes": getattr(r, 'notes', '')
        })
    for r in watch_qs:
        combined.append({
            "source": "watch",
            "recorded_at": r.recorded_at,
            "systolic": r.systolic,
            "diastolic": r.diastolic,
            "pulse": getattr(r, 'pulse', None),
            "notes": ''
        })

    # Sort ascending by datetime
    combined_sorted = sorted(combined, key=lambda x: x["recorded_at"])

    # Build labels and per-source maps using minute resolution
    labels = []
    manual_sys_map = {}
    manual_dia_map = {}
    watch_sys_map = {}
    watch_dia_map = {}

    for item in combined_sorted:
        label = item["recorded_at"].strftime("%Y-%m-%d %H:%M")
        if label not in labels:
            labels.append(label)
        if item["source"] == "manual":
            manual_sys_map[label] = item["systolic"]
            manual_dia_map[label] = item["diastolic"]
        else:
            watch_sys_map[label] = item["systolic"]
            watch_dia_map[label] = item["diastolic"]

    # Limit labels to last 50
    if len(labels) > 50:
        labels = labels[-50:]

    manual_systolic = [manual_sys_map.get(l, None) for l in labels]
    manual_diastolic = [manual_dia_map.get(l, None) for l in labels]
    watch_systolic = [watch_sys_map.get(l, None) for l in labels]
    watch_diastolic = [watch_dia_map.get(l, None) for l in labels]

    # merged_recent for the table (descending)
    merged_recent = sorted(combined, key=lambda x: x["recorded_at"], reverse=True)[:50]
    return render(request, "hypertension/bp_list.html", {
        "readings": merged_recent,
        # pass manual and watch arrays separately (do NOT merge)
        "labels_json": json.dumps(labels),
        "manual_systolic_json": json.dumps(manual_systolic),
        "manual_diastolic_json": json.dumps(manual_diastolic),
        "watch_systolic_json": json.dumps(watch_systolic),
        "watch_diastolic_json": json.dumps(watch_diastolic),
    })



@login_required
def manual_bp_graph(request: HttpRequest):
    """Render a dedicated manual BP graph (elder-friendly styling)."""
    Profile = _get_profile_model()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    manual_qs = BloodPressureReading.objects.filter(profile=profile).order_by("recorded_at")[:200]
    chart = list(manual_qs)
    labels = [r.recorded_at.strftime("%Y-%m-%d %H:%M") for r in chart]
    systolic = [r.systolic for r in chart]
    diastolic = [r.diastolic for r in chart]

    return render(request, "hypertension/manual_bp_graph.html", {
        "labels_json": json.dumps(labels),
        "systolic_json": json.dumps(systolic),
        "diastolic_json": json.dumps(diastolic),
    })


@login_required
def watch_bp_graph(request: HttpRequest):
    """Render a dedicated watch BP graph (elder-friendly styling)."""
    watch_qs = WatchBloodPressure.objects.filter(watch_sync__user=request.user).order_by("recorded_at")[:200]
    chart = list(watch_qs)
    labels = [r.recorded_at.strftime("%Y-%m-%d %H:%M") for r in chart]
    systolic = [r.systolic for r in chart]
    diastolic = [r.diastolic for r in chart]

    return render(request, "hypertension/watch_bp_graph.html", {
        "labels_json": json.dumps(labels),
        "systolic_json": json.dumps(systolic),
        "diastolic_json": json.dumps(diastolic),
    })


# ======================================================
#  BP: CREATE
# ======================================================
@login_required
def bp_create(request: HttpRequest):

    Profile = _get_profile_model()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BPReadingForm(request.POST)
        if form.is_valid():
            bp = form.save(commit=False)
            bp.profile = profile
            if not bp.recorded_at:
                bp.recorded_at = timezone.now()
            bp.save()
            messages.success(request, "Reading added successfully.")
            return redirect("hypertension:bp_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = BPReadingForm()

    return render(request, "hypertension/bp_form.html", {"form": form})


# ======================================================
#  BP: EDIT
# ======================================================
@login_required
def bp_edit(request: HttpRequest, pk: int):

    Profile = _get_profile_model()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    bp = get_object_or_404(BloodPressureReading, pk=pk, profile=profile)

    if request.method == "POST":
        form = BPReadingForm(request.POST, instance=bp)
        if form.is_valid():
            form.save()
            messages.success(request, "Reading updated.")
            return redirect("hypertension:bp_list")
        else:
            messages.error(request, "Fix errors.")
    else:
        form = BPReadingForm(instance=bp)

    return render(request, "hypertension/bp_form.html", {"form": form, "bp": bp})


# ======================================================
#  BP: DELETE
# ======================================================
@login_required
def bp_delete(request: HttpRequest, pk: int):

    Profile = _get_profile_model()
    profile, _ = Profile.objects.get_or_create(user=request.user)

    bp = get_object_or_404(BloodPressureReading, pk=pk, profile=profile)

    if request.method == "POST":
        bp.delete()
        messages.success(request, "Reading deleted.")
        return redirect("hypertension:bp_list")

    return render(request, "hypertension/bp_confirm_delete.html", {"bp": bp})


# ======================================================
#  SECTION PAGES
# ======================================================
@login_required
def bp_home(request):
    return render(request, "sections/bp_home.html")

@login_required
def medications_home(request):
    return render(request, "sections/medications_home.html")

@login_required
def salt_home(request):
    return render(request, "sections/salt_home.html")

@login_required
def food_home(request):
    return render(request, "sections/food_home.html")

@login_required
def devices_home(request):
    return render(request, "sections/devices_home.html")

@login_required
def reminders_home(request):
    return render(request, "sections/reminders_home.html")



@login_required
def connect_watch(request):
    """Sync the user's watch, persist a sample WatchBloodPressure reading, and redirect."""
    sync, created = WatchSync.objects.get_or_create(user=request.user)

    # Mark connected and update metadata
    sync.is_connected = True
    sync.device_name = "Hypertension SmartWatch"
    sync.battery_level = 90  # simulated battery
    sync.last_synced = timezone.now()
    sync.save()

    # Simulate receiving a watch-recorded blood pressure reading on sync.
    # Replace with real payload parsing when available.
    try:
        WatchBloodPressure.objects.create(
            watch_sync=sync,
            systolic=120,
            diastolic=78,
            pulse=72,
            recorded_at=timezone.now(),
            raw={}
        )
    except Exception:
        pass

    messages.success(request, "Watch synchronized successfully!")
    return redirect("hypertension:bp_list")
