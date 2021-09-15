# Generated by Django 3.2.6 on 2021-09-19 02:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0054_alter_user_language_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('is_seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created_at',),
                'permissions': (('manage_staff_event', 'Manage staff event.'),),
            },
        ),
    ]
