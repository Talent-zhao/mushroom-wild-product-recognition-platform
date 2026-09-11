from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_comment_sentiment_locked_commentblog_sentiment_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='predicthistory',
            name='time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='时间'),
        ),
        migrations.AlterField(
            model_name='predicthistory1',
            name='time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='时间'),
        ),
    ]
