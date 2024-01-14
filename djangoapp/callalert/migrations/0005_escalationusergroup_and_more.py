# Generated by Django 4.1.6 on 2024-01-14 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('callalert', '0004_alerthistory_call_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='EscalationUserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='escalation_user_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='callalert.escalationusergroup'),
        ),
    ]
