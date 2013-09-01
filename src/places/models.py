from django.db import models
import datetime


class Place(models.Model):
    vendor_id = models.CharField(max_length=50, unique=True)
    data = models.TextField()
