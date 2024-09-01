from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from multiselectfield import MultiSelectField
import uuid

class EnhancedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

TRIP_TYPES = [
    ('family', 'Family'),
    ('friends', 'Friends'),
    ('couple', 'Couple'),
    ('solo', 'Solo'),
    ('any', 'Any'),
]

TRIP_PREFERENCES = [
    ('adventure', 'Adventure Activities'),
    ('culture', 'Cultural Experiences'),
    ('nature', 'Nature & Wildlife'),
    ('relaxation', 'Relaxation'),
    ('culinary', 'Food & Culinary'),
    ('luxury', 'Luxury Travel'),
]

class TripPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input_id = models.UUIDField()
    user = models.CharField(max_length=50)
    itinerary = models.TextField()

class TripInput(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=50)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField()
    trip_type = models.CharField(choices=TRIP_TYPES, max_length=50)
    preferences = MultiSelectField(choices=TRIP_PREFERENCES)
    special_requests = models.TextField(blank=True)

class TripPlannerForm(forms.ModelForm):
    class Meta:
        model = TripInput
        fields = ['user', 'origin', 'destination', 'start_date', 'end_date', 'budget', 'adults', 'children', 'trip_type', 'preferences', 'special_requests']
        widgets = {
            'preferences': forms.CheckboxSelectMultiple,
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }

