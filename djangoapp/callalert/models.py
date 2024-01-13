from django.db import models

class alerthistory(models.Model):
    trigger_name = models.CharField(max_length=255, default='')
    trigger_severity = models.CharField(max_length=255, default='')
    destination_number = models.CharField(max_length=255, default='')  # Add default value
    timestamp = models.DateTimeField

    def __str__(self):
        return f"{self.trigger_name} - {self.trigger_severity}"
