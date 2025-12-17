# core/hypertension/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import BloodPressureReading


# -------------------------
#  Blood Pressure Form
# -------------------------
class BPReadingForm(forms.ModelForm):
    class Meta:
        model = BloodPressureReading
        # exclude recorded_at so view sets it server-side
        fields = ['systolic', 'diastolic', 'pulse', 'notes']


# -------------------------
#  Signup Form (Fix for error)
# -------------------------
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ("username", "email")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
