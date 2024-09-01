import os
import re
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_trip_plan(data):
    genai.configure(api_key=os.environ.get("GEN_AI_API"))
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Create a trip plan for {data.destination} from {data.start_date} to {data.end_date}. Group: {data.adults} adults, {data.children} children. Budget: {data.budget} INR. Type: {data.trip_type}. Preferences: {data.preferences}. Special requests: {data.special_requests}. Starting from: {data.origin}"
    response = model.generate_content([prompt], safety_settings=[
        {"category": cat, "threshold": "BLOCK_NONE"}
        for cat in ["HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
    ])
    return response.text

def get_main_city(location):
    genai.configure(api_key=os.environ.get("GEN_AI_API"))
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"If {location} is a city, return only its name. If not, return only its capital city name. No other text."
    response = model.generate_content([prompt])
    return response.text.strip()

def fetch_weather_forecast(location, data):
    api_key = os.environ.get("WEATHER_API")
    base_url = "http://api.weatherapi.com/v1"
    params = {'key': api_key, 'q': location, 'days': 3, 'aqi': 'no', 'alerts': 'no'}
    
    try:
        response = requests.get(f"{base_url}/forecast.json", params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        formatted_data = {
            'location': f"{weather_data['location']['name']}, {weather_data['location']['country']}",
            'current': {
                'temperature': {'celsius': weather_data['current']['temp_c'], 'fahrenheit': weather_data['current']['temp_f']},
                'condition': weather_data['current']['condition']['text'],
                'wind': {'speed': weather_data['current']['wind_kph'], 'direction': weather_data['current']['wind_dir']},
                'humidity': weather_data['current']['humidity'],
                'feels_like': {'celsius': weather_data['current']['feelslike_c'], 'fahrenheit': weather_data['current']['feelslike_f']},
            },
            'forecast': []
        }
        
        for day in weather_data['forecast']['forecastday']:
            formatted_data['forecast'].append({
                'date': day['date'],
                'description': day['day']['condition']['text'],
                'temperature': {'celsius': day['day']['avgtemp_c'], 'fahrenheit': day['day']['avgtemp_f']},
                'rain_chance': day['day']['daily_chance_of_rain'],
                'wind': {'speed': day['day']['maxwind_kph'], 'direction': day['hour'][12]['wind_dir']}
            })
        
        return formatted_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        return None