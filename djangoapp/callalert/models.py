from django.db import models


class alerthistory(models.Model):
    alert_date = models.DateTimeField('date alert generated')
    alert_text = models.CharField(max_length=1000)
    alert_recording = models.CharField(max_length=200)
    alert_receviers = models.CharField(max_length=200)

