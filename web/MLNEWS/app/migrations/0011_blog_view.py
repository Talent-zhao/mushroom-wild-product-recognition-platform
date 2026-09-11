from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_predicthistory_time_datetime_predicthistory1_time_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='view',
            field=models.PositiveIntegerField(default=0, verbose_name='浏览量'),
        ),
    ]
