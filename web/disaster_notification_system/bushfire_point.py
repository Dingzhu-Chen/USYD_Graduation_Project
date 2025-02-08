import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import math
from datetime import datetime, timedelta
import requests
import random
import os

def get_coordinates_within_radius(center_lat, center_lon, radius_km, spacing):
    km_to_deg_lat = 1 / 111 
    km_to_deg_lon = 1 / (111 * abs(math.cos(math.radians(center_lat))))
    
    # Convert radius from km to degrees
    radius_deg_lat = radius_km * km_to_deg_lat
    radius_deg_lon = radius_km * km_to_deg_lon
    
    # Generate coordinates within the radius
    coordinates = []
    
    # Create a grid of points within the specified radius
    for lat_offset in range(int(-radius_deg_lat/spacing), int(radius_deg_lat/spacing) + 1):
        for lon_offset in range(int(-radius_deg_lon/spacing), int(radius_deg_lon/spacing) + 1):
            lat = round(center_lat + lat_offset * spacing, 2)
            lon = round(center_lon + lon_offset * spacing, 2)
            
            # Calculate the distance from the center point
            distance = ((lat - center_lat)**2 + (lon - center_lon)**2)**0.5
            
            if distance <= radius_deg_lat:
                coordinates.append((lat, lon))
    
    return coordinates

def preprocess(json_data):
    data = pd.DataFrame(json_data)

    missing_values = data.isnull().sum()
    data = data.dropna()

    data['latitude'] = data['latitude'].round(2)
    data['longitude'] = data['longitude'].round(2)

    features_to_average = [
        'temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean',
        'apparent_temperature_max', 'apparent_temperature_min', 'apparent_temperature_mean',
        'daylight_duration', 'sunshine_duration', 'wind_direction_10m_dominant',
        'shortwave_radiation_sum'
    ]

    return data

def get_weather_data(coordinates):
    end_date = None
    if os.environ.get("development_date") == '1':
        end_date = datetime.strptime(os.environ.get("development_environment_date"), '%Y-%m-%d')
    else:
        end_date = datetime.today() - timedelta(days=4)

    past_date = end_date - timedelta(days=19)
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = past_date.strftime('%Y-%m-%d')

    # coordinates = [{'lat': -33.8688, 'lon': 151.2093}, {'lat': -37.8136, 'lon': 144.9631}]

    # Constructing the latitude and longitude parameters
    latitude_list = ",".join(str(coord[0]) for coord in coordinates)
    longitude_list = ",".join(str(coord[1]) for coord in coordinates)

    # Constructing the URL
    url = (f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={latitude_list}&longitude={longitude_list}&start_date={start_date}&end_date={end_date}&"
        "daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,apparent_temperature_max,"
        "apparent_temperature_min,apparent_temperature_mean,daylight_duration,sunshine_duration,"
        "wind_direction_10m_dominant,shortwave_radiation_sum")
   
    # Making the GET request
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        return data
    else:
        print(f"Error fetching data: {response.status_code}, {response.text}")
        return None

def convert_json_to_input_data(json_data):
  daily_data = json_data['daily']
#   latitude = [lat] * len(daily_data['time'])
#   longitude = [lon] * len(daily_data['time'])
  latitude = [json_data['latitude']] * len(daily_data['time'])
  longitude = [json_data['longitude']] * len(daily_data['time'])

  input_data = {
      "latitude": latitude,
      "longitude": longitude,
      "temperature_2m_max": daily_data['temperature_2m_max'],
      "temperature_2m_min": daily_data['temperature_2m_min'],
      "temperature_2m_mean": daily_data['temperature_2m_mean'],
      "apparent_temperature_max": daily_data['apparent_temperature_max'],
      "apparent_temperature_min": daily_data['apparent_temperature_min'],
      "apparent_temperature_mean": daily_data['apparent_temperature_mean'],
      "daylight_duration": daily_data['daylight_duration'],
      "sunshine_duration": daily_data['sunshine_duration'],
      "wind_direction_10m_dominant": daily_data['wind_direction_10m_dominant'],
      "shortwave_radiation_sum": daily_data['shortwave_radiation_sum']
  }
  input_data = pd.DataFrame(input_data)
  input_data = preprocess(input_data)
  return input_data

def predict_bushfire_point(json,coordinates):

    predictions = []
    with open('./disaster_notification_system/LSTM_smote_model.pkl', 'rb') as file:
        model = pickle.load(file)
        for i in range(len(coordinates)):
            data = convert_json_to_input_data(json[i])

            features = ['latitude', 'longitude', 'daylight_duration', 'sunshine_duration',
                    'shortwave_radiation_sum', 'wind_direction_10m_dominant',
                    'temperature_2m_min', 'apparent_temperature_max',
                    'temperature_2m_mean', 'apparent_temperature_min',
                    'temperature_2m_max', 'apparent_temperature_mean']

            X = data[features].values

            scaler = MinMaxScaler(feature_range=(0, 1))
            data_scaled = scaler.fit_transform(X)

            '''added'''
            #n_components = min(min(data_scaled.shape), 6)
            #pca = PCA(n_components=n_components)
            pca = PCA(n_components=6)
            data_pca = pca.fit_transform(data_scaled)

            X_input = data_pca.reshape(1, 20, 6)
            #X_input = data_pca.reshape(1, data_pca.shape[0], n_components)

            prediction = model.predict(X_input)[0][0]
            # predictions.append([coordinates[i][0],coordinates[i][1],prediction])
            predictions.append([json[i]['latitude'],json[i]['longitude'],prediction])

    return predictions

def bushfire_points(lat,lon):
    
    radius_km = 5
    spacing = 0.01 

    coordinates =  get_coordinates_within_radius(lat, lon, radius_km, spacing)
    json = get_weather_data(coordinates)
    return predict_bushfire_point(json,coordinates)



# def get_suburb_name(latitude, longitude):
#     # Define the endpoint URL
#     API_KEY = os.environ.get("Google_API_key")
#     url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={API_KEY}&language=en"

#     # Make the GET request
#     response = requests.get(url)

#     # Check if the request was successful
#     if response.status_code == 200:
#         data = response.json()

#         # Check if any results were returned
#         if data['results']:
#             i=0
#             res = 'None'
#             while i < 2:
#                 for component in data['results'][i]['address_components']:
#                     # Look for the 'sublocality' or 'locality' type for suburb name
#                     if 'sublocality' in component['types'] or 'locality' in component['types']:
#                         res = component['long_name']
#                         break
#                 i+=1
#             return res
#         else:
#             return "No results found."
#     else:
#         return f"Error: {response.status_code} - {response.text}"



# coordinates =  get_coordinates_within_radius(lat, lon, radius_km, spacing)
# coordinates = [(-33.89, 150.78),(-34.24, 149.93),(-34.41, 150.60)]
# json = get_weather_data(coordinates)
# print(predict_bushfire_point(json,coordinates))

# print(get_firms_bushfire())