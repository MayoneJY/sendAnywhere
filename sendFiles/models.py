from django.db import models

class File(models.Model):
    file = models.FileField(upload_to='files/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    file_password = models.CharField(max_length=100)
