# Generated by Django 3.0.5 on 2020-05-10 17:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tumblr_posts', '0002_auto_20200502_1831'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='blog_name',
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blog_name', models.CharField(max_length=255, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('is_primary', models.BooleanField()),
                ('avatar', models.URLField()),
                ('followers', models.IntegerField()),
                ('posts', models.IntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='blog',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tumblr_posts.Blog'),
            preserve_default=False,
        ),
    ]
