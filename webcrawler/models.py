from django.db import models

class CrawlResult(models.Model):
    url = models.URLField()
    status_code = models.IntegerField()
    content = models.TextField()
    crawled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url