from django.db import models
import random as rand
from user.models import User
from user.models import Property
from django.contrib.gis.db import models as geomodels

class Bushfire(geomodels.Model):
    BUSHFIRE_TYPE_CHOICES = [
        ('firms', 'Real Bushfire'),
        ('predicted', 'Predicted Bushfire'),
    ]

    location = geomodels.CharField(max_length=255, null=True)
    category = geomodels.CharField(max_length=10, choices=BUSHFIRE_TYPE_CHOICES)
    geometry = geomodels.PointField(null=False)
    acquire_date = geomodels.CharField(max_length=16, null=False)
    acquire_time = geomodels.CharField(max_length=16, null=True)
    parent_id = geomodels.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True,
        related_name='predicted_bushfires'
    )

    class Meta:
        unique_together = ('category','geometry', 'acquire_date')

