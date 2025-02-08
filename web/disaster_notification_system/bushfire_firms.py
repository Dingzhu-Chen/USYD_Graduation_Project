
import pandas as pd
import requests
import asyncio
import aiohttp
import time
from .models import Bushfire
from django.contrib.gis.geos import Point
import os
from datetime import datetime

def get_firms_bushfire():
    API_KEY = os.environ.get("Firms_API_key")
    query_date = ""
    if os.environ.get("development_date") == '1':
        query_date = os.environ.get("development_environment_date")
    else:
        query_date = datetime.today().strftime('%Y-%m-%d')
    url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/"+API_KEY+"/MODIS_NRT/AUS/1/"+query_date
    
    # Read bushfire data into DataFrame
    df = pd.read_csv(url)

    coords = [(row['latitude'], row['longitude']) for _, row in df.iterrows()]
    
    bushfire_data = []
    
    batch_index = 0
    results = asyncio.run(batch_geocode(coords))
    
    if results:
        i = 0
        while i < len(coords):
            geometry = Point(coords[i][1], coords[i][0], srid=4326)
            location = extract_locality(results[i])

            s = str(df.iloc[i]['acq_time']).zfill(4)
    
            hours = s[:-2] 
            minutes = s[-2:]
            
            # Return formatted string
            time = f"{hours}:{minutes}"

            date = df.iloc[i]['acq_date']
            
            try:
                Bushfire.objects.get_or_create(
                    location=location,
                    category='firms',
                    geometry=geometry,
                    acquire_date=date,
                    acquire_time=time
                )
            except IntegrityError:
                # Handle the case where there's a unique constraint violation
                print(f"Duplicate entry found for date {date} and time {time}. Skipping...")

            i+=1

def extract_locality(response):
    for result in response.get('results', []):
        for component in result.get('address_components', []):
            if 'locality' in component.get('types', []):
                return component.get('long_name')
    return None

async def geocode_coordinate(session, lat, lng):
    API_KEY = os.environ.get("Google_API_key")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={API_KEY}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            print(f"Failed request for {lat},{lng}: Status {response.status}")
            return None

async def batch_geocode(coordinates, batch_size=50):
    semaphore = asyncio.Semaphore(batch_size)  # Limit to 50 concurrent requests

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Inner function to acquire semaphore and make the request
        async def limited_geocode(lat, lng):
            async with semaphore:
                return await geocode_coordinate(session, lat, lng)

        for lat, lng in coordinates:
            task = asyncio.create_task(limited_geocode(lat, lng))
            tasks.append(task)

        # Process tasks with a delay to enforce google geocoding API rate limits (50 requests per second)
        results = []
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            # Wait for all requests in the current batch to complete
            results += await asyncio.gather(*batch)
            # Introduce a delay to avoid exceeding 50 requests per second
            time.sleep(1)

        return results

