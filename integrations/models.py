from django.db import models


# Create your models here.
class Integration(models.Model):
    name = models.CharField(max_length=200)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    redirect_uri = models.CharField(max_length=255, blank=True, null=True)
    authorization_code = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    api_key = models.CharField(max_length=200, blank=True, null=True)
    instance_id = models.CharField(max_length=200, blank=True)
    auth_json = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=False)
    expire_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync_at = models.DateTimeField(null=True)
