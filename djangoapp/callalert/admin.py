from django.contrib import admin
from .models import *

@admin.register(alerthistory)
class alerthistory(admin.ModelAdmin):
    list_display = ('trigger_name', 'trigger_severity', 'timestamp', 'details', 'call_source')

@admin.register(EscalationUserGroup)
class EscalationUserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_users')

    def display_users(self, obj):
        return ", ".join([user_profile.user.username for user_profile in obj.userprofile_set.all()])

    display_users.short_description = 'Users'

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_shifts', 'escalation_user_group')

    def display_shifts(self, obj):
        return ', '.join([shift.name for shift in obj.shifts.all()])
    
    display_shifts.short_description = 'Shifts'

@admin.register(OnCallDuty)
class OnCallDutyAdmin(admin.ModelAdmin):
    list_display = ('user', 'duty')
