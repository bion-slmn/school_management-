# Generated by Django 4.2.10 on 2024-06-08 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students',
            name='course_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='student_management_app.courses'),
        ),
    ]