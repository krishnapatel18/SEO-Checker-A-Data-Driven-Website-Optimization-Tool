from django.urls import path
from .views import crawl

urlpatterns = [
    path('crawl/', crawl, name='crawl'),
]