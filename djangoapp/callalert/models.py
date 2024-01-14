from django.db import models
from django.contrib.auth.models import User

class alerthistory(models.Model):
    trigger_name = models.CharField(max_length=255, default='')
    trigger_severity = models.CharField(max_length=255, default='')
    destination_number = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    call_source = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.trigger_name} - {self.trigger_severity}"

class EscalationUserGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
        
class Shift(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    escalation_user_group = models.ForeignKey(EscalationUserGroup, on_delete=models.SET_NULL, null=True, blank=True)
    shifts = models.ManyToManyField(Shift)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.user.username

class OnCallDuty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    duty = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - On Duty: {self.duty}"