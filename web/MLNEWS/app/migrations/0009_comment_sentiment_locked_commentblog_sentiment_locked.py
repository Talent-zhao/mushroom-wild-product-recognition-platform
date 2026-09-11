from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_comment_sentiment_commentblog_sentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='sentiment_locked',
            field=models.BooleanField(default=False, verbose_name='情感已人工确认'),
        ),
        migrations.AddField(
            model_name='commentblog',
            name='sentiment_locked',
            field=models.BooleanField(default=False, verbose_name='情感已人工确认'),
        ),
    ]

