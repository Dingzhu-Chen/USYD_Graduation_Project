import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import pickle
from disaster_notification_system.bushfire_point import convert_json_to_input_data, get_coordinates_within_radius
from .models import Bushfire
from datetime import datetime, timedelta
import requests
from django.contrib.gis.geos import Point
import os

def predict_bushfire_path_3days(json_data, timesteps=3):

    model_path="./disaster_notification_system/SOS_surrounding3days_1output.pkl"

    with open(model_path, 'rb') as file:
        model = pickle.load(file)
        # Define MinMaxScaler and PCA (n_components=6)
        scaler = MinMaxScaler(feature_range=(0, 1))  # Directly define scaler
        pca = PCA(n_components=6)  # Directly define PCA with 6 components

        # Prepare data for prediction
        if isinstance(json_data, dict):
            json_data = [json_data]  # Convert dict to list for consistency

        # Initialize a list to store results for each future day
        future_days_results = []


        for data_item in json_data:  # Iterate through json_data items directly
            # Convert json_data into a dataframe
            data = convert_json_to_input_data(data_item)

            # Ensure the necessary features are present
            features = ['daylight_duration', 'sunshine_duration', 'shortwave_radiation_sum',
                        'wind_direction_10m_dominant', 'temperature_2m_min',
                        'apparent_temperature_max', 'temperature_2m_mean',
                        'apparent_temperature_min', 'temperature_2m_max',
                        'apparent_temperature_mean']
            # Reshape data to 2D for DataFrame creation
            num_days = len(data['daylight_duration']) # Get number of days
            X = data[features].values.reshape(num_days, len(features))

            # Scale and transform data using MinMaxScaler and PCA
            scaler = MinMaxScaler(feature_range=(0, 1))
            X_scaled = scaler.fit_transform(X)
            pca = PCA(n_components=6)
            X_pca = pca.fit_transform(X_scaled)

            # Create sequences for LSTM (timesteps are 3, as defined)
            def create_sequences(X, timesteps):
                X_seq = []
                for i in range(len(X) - timesteps + 1):
                    X_seq.append(X[i:i + timesteps])
                return np.array(X_seq)

            X_seq = create_sequences(X_pca, timesteps)

            # Predict using the trained LSTM model
            predictions = model.predict(X_seq)

            # Assuming the model outputs one set of predictions for each timestep starting from the next day
            results = []
            for day in range(timesteps):
                # Get the prediction for the current day
                current_day_prediction = predictions[0][day] if predictions.ndim > 2 else predictions[day]

                # Accessing the output values for the current day
                predicted_output = int(current_day_prediction[0] > 0.5)  # Fire/no fire (binary classification)

                results.append({
                    'output': predicted_output
                })

            # Store results for each input data point
            future_days_results.append(results)

    return future_days_results

def get_weather_data(coordinates):
    end_date = None
    if os.environ.get("development_date") == '1':
        end_date = datetime.strptime(os.environ.get("development_environment_date"), '%Y-%m-%d')
    else:
        end_date = datetime.today()

    past_date = end_date - timedelta(days=6)
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

def predict_path():

    Bushfire.objects.filter(category="path").delete() # clear past path prediction

    query_date = ""
    if os.environ.get("development_date") == '1':
        query_date = os.environ.get("development_environment_date")
    else:
        query_date = datetime.today().strftime('%Y-%m-%d')
    busfhires = Bushfire.objects.filter(acquire_date=query_date)[:50] # for demostration only, since weather api has limit
    coordinates_real = []
    bushfire_map = {}  # Create a dictionary to map original coordinates to disaster instances

    for bushfire in busfhires:
        coordinates = (bushfire.geometry.y, bushfire.geometry.x)
        coordinates_real.append(coordinates)
        bushfire_map[coordinates] = bushfire
    # Get path predictions based on the weather data
    for coord in coordinates_real:
        coords = get_coordinates_within_radius(coord[0],coord[1],3,0.01) #predict in 3km radius
        we = get_weather_data(coords)
        predictions = predict_bushfire_path_3days(we)

        # Match predictions with the busfhires based on original coordinates
        for original_coord in coords:
            lat = original_coord[0]
            lon = original_coord[1]
            for p in predictions:
                index = 0
                while index < len(p):
                    prediction = p[index]

                    if coord in bushfire_map:
                        bushfire = bushfire_map[coord]  # Get the corresponding disaster object
                        # Check if the the predicted bushfire path existed
                        if prediction['output'] == 1:
                            geometry = Point(lon,lat)
                            acquire_date = None
                            if os.environ.get("development_date") == '1':
                                acquire_date = datetime.strptime(os.environ.get("development_environment_date"), '%Y-%m-%d') + timedelta(days=index+1)
                            else:
                                acquire_date = datetime.today().strftime('%Y-%m-%d') + timedelta(days=index+1)
                            acquire_date = acquire_date.strftime('%Y-%m-%d')

                            # Check if a bushfire with the same geometry and acquire_date already exists
                            predicted_bushfire, created = Bushfire.objects.get_or_create(
                                category='path',
                                geometry=geometry,
                                acquire_date=acquire_date
                            )

                            # If it already exists (not created), add the current bushfire to the parent_id
                            if not created:
                                predicted_bushfire.parent_id.add(bushfire)
                            else:
                                predicted_bushfire.parent_id.add(bushfire)
                                predicted_bushfire.save()
                    index += 1
