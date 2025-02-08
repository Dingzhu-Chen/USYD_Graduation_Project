# CS45 - Bushfire Path Algorithm with Bushfire Warning System

**8th August 2024 - 25th October 2024**

## PROJECT OVERVIEW

This project provided aims to mitigate the risk for farmers who may be impacted by bushfires as Australia is one of the countries most heavily impacted by bushfires. To achieve the objective, two AI models with advanced machine learning techniques is built to predict the bushfire start location and its location after spread. Both bushfire start location and path model will be trained by historical bushfire related data. The source code contain a web application with the model deployed which visualize the predicted bushfires on an interactive map for users to analyze the risk that their property may be impacted. Furthermore, users will receive notification based on the their stored property(home, office or farm, etc.) to notify that these places are in danger of being impacted by bushfires. 

To speed up development progress, OreFox provided a [Natural Disaster Warning System][Reaction_QLD] for QLD which is developed by Team Reaction of QUT, this project has similar scope and features to our project, some of the work are referred and integrate into our system, we develop our application based on their structure. 

[Reaction_QLD]:https://github.com/OreFox/Reaction_QUT


## SET UP INSTRUCTIONS

### Additional Packages
Beside the packages required on Reaction_QUT project, we requires some new packages/ updated packages including:
- aiohttp
- tensorflow version 2.17.0

all packages are listed on requirements.txt

### Instruction Manual

#### APIs & Environment file
Following APIs are required, please sign up to obtain api key for each of them:

- [NASA Firms map key][NASA_FIRMS]
- [Google Map API Key (follow guides to enable apis: Geocoding API, Places API, Geolocation API, Maps JavaScript API)][Google]

[NASA_FIRMS]:https://firms.modaps.eosdis.nasa.gov/api/map_key/
[Google]:https://developers.google.com/maps/documentation/javascript/get-api-key

Put the api keys in .env and please provide an email address on DEV_EMAIL for receiving email for development use.
  
![Screenshot 2024-10-23](https://i.imgur.com/oFdCUsy.png)

<!-- - Then go to your virtual environment folder (venv) outside the web folder and move to `venv -> Lib -> djconfig -> admin.py` and edit line 29.
  	Change
                  `from django.conf.urls import url`
        to
                  `from django.urls import re_path as url` -->

In addition, the google map api has to be filled manually here: web/user/templates/user/properties_add_edit.html

![Screenshot 2024-10-24](https://i.imgur.com/NehRVWG.png)
![Screenshot 2024-10-21](https://i.imgur.com/JGChSRg.png)

In the get_disaster_interactive_map.js inside disaster_notification_system module, put the [windy api][windy] key here

![Screenshot 2024-10-21](https://i.imgur.com/kWcPW7o.png)

[windy]:[https://api.windy.com/]

#### Celery
Once the postgis database and python virtual environment are setup. Celery has to be launched to control the scheduled email notification task. For the system to work, two Celery services need to be run. From within the `/web` directory, you can run the main Celery worker, which is used to run the notification tasks, using the following command, adjust the logging level as needed:

```shell
celery -A main worker --loglevel=info
```

Celery Beat is also required to be running as this service is used to schedule the bushfire data gathering task and notification task so that they can be automatically run at specific times instead of being manually triggered. When it runs, it will obtaining bushfire data and required weather data from api, then bushfire prediction process will be started and be stored into database, if high risk bushfire is detected around user property, notification will be sent. This can be run using the following command:

```shell
celery -A main beat --loglevel=info
```

To trigger the scheduled task manually, you can run the following command from the `/web` directory:

```shell
celery -A main call disaster_notification_system.tasks.get_daily_bushfire
```

Since the scheduled task is on 0:00 everyday, there is no data inside database when launching this application at first time, please run this command manually once first to load data into database so that functionalities can working.


#### Final Steps
```
cd web
python manage.py runserver
```
#### Installation Video

## Usage Instruction

### Main Components

0. scheduled task work flow 
Scheduled task will be run per day which contain following processes: 

    - predict if there will be bushfire start around user's property.
    - get today bushfire date from nasa firms api.
    - predict where the real bushfire and predicted bushfire mentioned above will spread, based on the prediction    result.
    - trigger email notification sending process if the real bushfire or predicted bushfire shows inside 5km radius from the user's property.

1. Property Management
    Allow user to store their property information into the system. In addition, user can decide whether to receive email notification on a property, edit or delete stored properties.

    ![Screenshot 2024-10-24](https://i.imgur.com/CxlnXzj.png)
    
    For property creation, user have to set a name for the property and input the address. The auto-fill functionality is developed for user to input their address easily and user can just use their current location if they want as well, the address will be input into the textbox automatically by doing that.

    ![Screenshot 2024-10-24](https://i.imgur.com/hPBQAUw.png)

2. Dashboard
    User have a quick view to some useful information including the recent bushfire and weather information of popular cities in Australia. Furthermore, user can check out the bushfire on map by clicking the check on map button.

    ![Screenshot 2024-10-24](https://i.imgur.com/xKXrMWr.png)

3. Interactive map
    An interactive map shows all real bushfires and predicted bushfires in red triangle icon and yellow triangle icon, the stored property location will be displayed on map with a blue icon as well. 

    ![Screenshot 2024-10-24](https://i.imgur.com/zpbZjpi.png)

4. buttons on map
    First button pop up a modal window display all stored property of this user and a button to navigate user to property management page, check on map button next to each properties.

    ![Screenshot 2024-10-24](https://i.imgur.com/9h2yr56.png)

    Second button open a modal window display all real bushfire obtained from api as a list with check on map buttons.

    ![Screenshot 2024-10-24](https://i.imgur.com/8AtvCei.png)

    Third button will navigate to user's current position on map so that they can check out if there is bushfire around them.

    Fourth button is used for switch visualization of predicted bushfire in 1/2/3 day later. In the screenshot, the bushfire predicted exist in 2 days later but disappear in third day.

    ![Screenshot 2024-10-24](https://i.imgur.com/EspLRKg.png)

    ![Screenshot 2024-10-24](https://i.imgur.com/C08BXGe.png)

### Unstable Features/ Limitations