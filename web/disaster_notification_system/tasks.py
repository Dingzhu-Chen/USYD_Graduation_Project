from celery import shared_task
from user.models import User, Property
from django.core.mail import send_mail
import json
import os
import datetime
from disaster_notification_system.bushfire_point import bushfire_points
from django.conf import settings
from django.utils.timezone import now
from django.db import IntegrityError
from disaster_notification_system.bushfire_firms import get_firms_bushfire
from disaster_notification_system.bushfire_path import predict_path
from datetime import datetime
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from datetime import datetime, timedelta

sendToRealEmails = True
devEmail = os.environ.get('DEV_EMAIL')
all_users = User.objects.all()

@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 10}, retry_backoff=True)
def sendNotificationEmail(userId, hazardsTable):
    if len(hazardsTable) == 0:
        return
    user_by_id = User.objects.get(id=userId)
    context = emailContext(user_by_id, hazardsTable)
    email_html = emailHTML(context)
    email = emailMessage(user_by_id, email_html)
    email.send()

def bushfire_point_prediction():
    for user in all_users:
        for p in Property.objects.filter(user = user):
            if p.geometry != Point(0,0):
                longitude, latitude = p.geometry.x, p.geometry.y
                predictions = bushfire_points(float(latitude), float(longitude))
                for prediction in predictions:
                    if prediction[2] >= 0.8:
                        save_prediction(p.id, prediction[0], prediction[1])

def bushfire_notifications_task():
    for user in all_users:
        alerting_properties=[]
        for p in Property.objects.filter(user = user):
            appended = False
            if p.geometry != Point(0,0):
                if find_nearby_bushfires(p).exists() and p.receive_alert and not appended:
                    alerting_properties.append(p.name)
                    appended = True

        if len(alerting_properties) != 0:
            send_notification_email(alerting_properties)


def find_nearby_bushfires(property):
    user_location = property.geometry 
    nearby_bushfires = Bushfire.objects.filter(
        geometry__distance_lte=(user_location, D(km=5))  # Find within 5 km
    ).annotate(distance=Distance('geometry', user_location)).order_by('distance')

    return nearby_bushfires

@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 10}, retry_backoff=True)
def get_daily_bushfire():
    bushfire_point_prediction()
    get_firms_bushfire()
    predict_path()
    bushfire_notifications_task()

def save_prediction(property_id, lat, lon):

    property_instance = Property.objects.get(id=property_id)
    geometry = Point(lon, lat, srid=4326)

    acquire_date = None
    if os.environ.get("development_date") == '1':
        acquire_date = datetime.strptime(os.environ.get("development_environment_date"), '%Y-%m-%d')
        acquire_date = acquire_date + timedelta(days=1)
    else:
        acquire_date = datetime.today()

    acquire_date = acquire_date.strftime('%Y-%m-%d')
    try:
        Bushfire.objects.get_or_create(
            category = "predicted",
            geometry = geometry,
            acquire_date = acquire_date,
        )
    except IntegrityError:
        pass

def send_notification_email(properties):
    subject = "Bushfire Alert!"
    message = "These properties may affected by bushfire: "
    for p in properties:
        message += str(p) + " "
    
    send_mail(
        subject,  
        message, 
        settings.EMAIL_HOST_USER, 
        [devEmail],  
        fail_silently=False,
    )

async def sendBannerNotifications(userId, notificationsDict):
    channel_name = f"user_{str(userId)}"
    await channel_layer.group_send(
        channel_name,
        {
            "type": "disasterNotification",
            "message": json.dumps(notificationsDict),
        },
    )

# get_daily_bushfire()
# bushfire_notifications_task()
# predict_path()