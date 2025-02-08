import os
import json
from . import tasks
from . import weather
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from datetime import datetime, date
from user.models import Property
from .models import Bushfire
from django.contrib.gis.geos import Point

def disaster_notification_system(request):

    return render(request, 'disaster_notification_system/disaster_interactive_map.html', {})

def get_recent_bushfires(request):
    query_date = ""
    if os.environ.get("development_date") == '1':
        query_date = os.environ.get("development_environment_date")
    else:
        query_date = datetime.today().strftime('%Y-%m-%d')
    bushfires = Bushfire.objects.filter(category="firms", acquire_date=query_date)
    bushfire_data = []
    for bushfire in bushfires:
        bushfire_entry = {
            "location": bushfire.location,
            "startDate": bushfire.acquire_date,
            "startTime": bushfire.acquire_time,
            "coordinates": {
                "latitude": bushfire.geometry.y,
                "longitude": bushfire.geometry.x,
            }
        }
        bushfire_data.append(bushfire_entry)
    return JsonResponse(bushfire_data, safe=False)

def get_weather_data(request):
    weather_data = weather.get_weather_data()
    return JsonResponse(weather_data, safe=False)

@login_required
def get_user_properties(request):
    properties = Property.objects.filter(user=request.user)
    features = []

    for property in properties:
        if property.geometry and property.geometry != Point(0,0):

            geojson_point = {
                "type": "Point",
                "coordinates": [property.geometry.x, property.geometry.y]
            }
            features.append({
                'type': 'Feature',
                'geometry': geojson_point,
                'properties': {
                    'name': property.name,
                    'address': property.address,
                }
            })

    geojson_data = {
        'type': 'FeatureCollection',
        'features': features
    }
    return JsonResponse(geojson_data)

@login_required
def get_predicted_bushfire(request):
    predicted_bushfire = Bushfire.objects.filter(category="predicted")
    features = []

    for p in predicted_bushfire:
        if p.geometry != Point(0,0):

            geojson_point = {
                "type": "Point",
                "coordinates": [p.geometry.x, p.geometry.y]
            }

            features.append({
                'type': 'Feature',
                'geometry': geojson_point,
                'properties': {
                    'name': "",
                    'address': "",
                }
            })
    geojson_data = {
        'type': 'FeatureCollection',
        'features': features
    }
    # print(geojson_data)
    return JsonResponse(geojson_data)

@login_required
def get_path(request):
    busfhires = Bushfire.objects.filter(category='path')
    features=[]

    for p in busfhires:
        if p.geometry != Point(0,0):

            parents = []

            parent_bushfires = p.parent_id.all()

            for parent_bushfire in parent_bushfires:
                parent_geometry = parent_bushfire.geometry
                geo = {
                    "type": "Point",
                    "coordinates": [parent_geometry.x, parent_geometry.y]
                }
                parents.append(geo)

            geojson_point = {
                "type": "Point",
                "coordinates": [p.geometry.x, p.geometry.y]
            }

            today = None
            if os.environ.get("development_date") == '1':
                today = datetime.strptime(os.environ.get("development_environment_date"), '%Y-%m-%d')
            else:
                today = datetime.today()
            date = datetime.strptime(p.acquire_date, '%Y-%m-%d')
            difference = (date - today).days # check it is day 1/2/3

            features.append({
                'type': 'Feature',
                'geometry': geojson_point,
                'properties': {
                    'name': "",
                    'address': "",
                },
                'day': difference,
                'parents': parents
            })
    geojson_data = {
        'type': 'FeatureCollection',
        'features': features
    }
    return JsonResponse(geojson_data)
