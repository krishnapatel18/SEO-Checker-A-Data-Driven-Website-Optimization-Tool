from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    plan = models.CharField(max_length=20, default='Free') 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# Signin model 
class Signin(models.Model):
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

# Signup model
class Signup(models.Model):
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

# Home model (if needed)
class Home(models.Model):
    pass

# Profile model
class Profile(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    company = models.CharField(max_length=255)

# Change Password model
class ChangePassword(models.Model):
    email = models.CharField(max_length=255)
    new_password = models.CharField(max_length=255)
    confirm_password = models.CharField(max_length=255)

# Project model
class Project(models.Model):
    url = models.URLField()

# Website model
class Website(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()

# SEO Analysis model
class SEOAnalysis(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    seo_suggestions = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

# Crawl Result model
class CrawlResult(models.Model):
    url = models.URLField()
    status_code = models.IntegerField()
    content = models.TextField()
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    seo_suggestions = models.TextField(blank=True, null=True)
    response_time = models.FloatField(blank=True, null=True)
    file_size = models.FloatField(blank=True, null=True)
    word_count = models.IntegerField(blank=True, null=True)
    media_files = models.IntegerField(blank=True, null=True)
    internal_links = models.IntegerField(blank=True, null=True)
    external_links = models.IntegerField(blank=True, null=True)
    backlinks = models.TextField(blank=True, null=True)
    page_speed_insights = models.TextField(blank=True, null=True)
    suggested_keywords = models.TextField(blank=True, null=True)
    crawled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
