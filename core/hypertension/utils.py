# hypertension/utils.py
"""
ACC/AHA-only BP classification helper (elder-friendly).

Function:
    classify_bp(systolic:int, diastolic:int) -> (label, badge, advice, severity)

 - label: human label
 - badge: bootstrap color (success, info, warning, danger, dark)
 - advice: short elder-friendly sentence to show on dashboard
 - severity: simple key ('normal','elevated','stage1','stage2','urgency','emergency','unknown')
"""
from typing import Tuple

def classify_bp(systolic: int, diastolic: int) -> Tuple[str, str, str, str]:
    # coerce to ints where possible
    try:
        s = int(systolic)
        d = int(diastolic)
    except Exception:
        return ("Invalid reading", "dark", "Reading error — please re-enter.", "unknown")

    # 1. Highest priority: emergency
    if s >= 180 or d >= 120:
        return ("Hypertensive Emergency", "danger",
                "Very high blood pressure — get emergency help now.", "emergency")

    # 2. Urgency (severe, no organ damage assumed)
    # We'll treat >=180 or >=110 as urgent, but emergency already handled above.
    if s >= 180 or d >= 110:
        return ("Hypertensive Urgency", "danger",
                "Extremely high blood pressure — contact healthcare immediately.", "urgency")

    # ACC/AHA classification (2017) — elder-friendly mapping
    # Normal
    if s < 120 and d < 80:
        return ("Normal", "success",
                "Your blood pressure is in the normal range. Keep healthy habits.", "normal")

    # Elevated
    if 120 <= s <= 129 and d < 80:
        return ("Elevated", "info",
                "Slightly raised. Try salt reduction, walking, and avoid smoking.", "elevated")

    # Stage 1
    if (130 <= s <= 139) or (80 <= d <= 89):
        return ("Stage 1 Hypertension", "warning",
                "Mild high blood pressure — check with your doctor and try lifestyle changes.", "stage1")

    # Stage 2
    if s >= 140 or d >= 90:
        return ("Stage 2 Hypertension", "danger",
                "High blood pressure — see a doctor. Medication may be needed.", "stage2")

    # fallback
    return ("Uncertain", "dark", "Unable to classify. Please re-check your reading.", "unknown")
