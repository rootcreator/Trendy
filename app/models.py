from django.contrib.auth.models import User
from django.db import models

class TrendCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Trend(models.Model):
    CATEGORY_CHOICES = [
        ('entertainment', 'Entertainment'),
        ('lifestyle', 'Lifestyle'),
        ('technology', 'Technology'),
        ('food_and_drink', 'Food and Drink'),
        ('sports', 'Sports'),
        ('politics', 'Politics'),
        ('business', 'Business'),
        ('education', 'Education'),
        ('science', 'Science'),
        ('arts_and_culture', 'Arts and Culture'),
    ]
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    cover_picture_url = models.URLField(blank=True, null=True)
    url = models.URLField()
    source = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(TrendCategory, blank=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/',  null=True, blank=True)
    preferred_categories = models.ManyToManyField('TrendCategory', blank=True)

    def __str__(self):
        return self.user.username


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trend_title = models.CharField(max_length=255)
    trend_url = models.URLField()
    trend_source = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'trend_url')


