from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import EnhancedUserCreationForm, TripPlannerForm, TripInput, TripPlan
from .services import create_trip_plan, fetch_weather_forecast, get_main_city
from .auth_helpers import require_auth, require_guest

def home(request):
    return render(request, 'index.html')

@require_guest
def signup(request):
    if request.method == 'POST':
        form = EnhancedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = EnhancedUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

@require_guest
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@require_auth
def dashboard(request):
    trips = TripInput.objects.filter(user=request.user.username).values()
    return render(request, 'dashboard.html', {'trips': trips})

@require_auth
def plan_trip(request):
    if request.method == 'POST':
        form = TripPlannerForm(request.POST)
        if form.is_valid():
            trip_data = form.save()
            itinerary = create_trip_plan(trip_data)
            weather_data = fetch_weather_forecast(get_main_city(trip_data.destination), trip_data)
            TripPlan.objects.create(input_id=trip_data.id, user=trip_data.user, itinerary=itinerary)
            
            context = {'trip': trip_data, 'itinerary': itinerary, 'weather': weather_data}
            return render(request, 'trip/details.html', context)
    else:
        form = TripPlannerForm(initial={'user': request.user.username})
    return render(request, 'trip/planner.html', {'form': form})

@require_auth
def view_trip(request, trip_id):
    trip_input = TripInput.objects.get(id=trip_id)
    trip_plan = TripPlan.objects.get(input_id=trip_id)
    weather_data = fetch_weather_forecast(get_main_city(trip_input.destination), trip_input)
    context = {'trip': trip_input, 'itinerary': trip_plan.itinerary, 'weather': weather_data}
    return render(request, 'trip/details.html', context)

@require_auth
def clear_trips(request):
    TripInput.objects.filter(user=request.user.username).delete()
    TripPlan.objects.filter(user=request.user.username).delete()
    return redirect('dashboard')

@require_auth
def delete_trip(request, trip_id):
    TripInput.objects.get(id=trip_id).delete()
    TripPlan.objects.filter(input_id=trip_id).delete()
    return redirect('dashboard')

def contact(request):
    return render(request, 'contact.html')