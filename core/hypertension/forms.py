# core/hypertension/forms.py
from django import forms
from .models import BloodPressureReading

class BPReadingForm(forms.ModelForm):
    class Meta:
        model = BloodPressureReading
        # exclude recorded_at so view sets it server-side and avoids NOT NULL db errors
        fields = ['systolic', 'diastolic', 'pulse', 'notes']
