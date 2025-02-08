import aiohttp
import asyncio

async def get_weather(session, city):
    api_key = '6d630bafd48349e4b8613148242509' 
    url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no'
    
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()

            return {"city": city, "weather": data['current']['condition']['text'], 
                    "maxTemperature": data["forecast"]["forecastday"][0]["day"]["maxtemp_c"], 
                    "minTemperature": data["forecast"]["forecastday"][0]["day"]["mintemp_c"]}
    
    except aiohttp.ClientResponseError as err:
        print(f"HTTP error occurred: {err}")

async def get_weather_cities():
    cities = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Hobart"]
    res = []

    async with aiohttp.ClientSession() as session:
        tasks = [get_weather(session, city) for city in cities]
        res = await asyncio.gather(*tasks)  # Gather the results of all tasks
    
    return res

def get_weather_data():
    weather_data = asyncio.run(get_weather_cities())

    return weather_data