from django.db import models

# Create your models here.
class Template(models.Model):
    module = models.CharField(max_length=200, blank=True, null=True)
    app = models.CharField(max_length=200, blank=True, null=True)
    obj_type = models.CharField(max_length=200, blank=True)
    schema = models.TextField(blank=True, null=True)
    chunking_type = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    account_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)