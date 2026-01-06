from django.db import models


class ScriptAuth(models.Model):
    """
    One auth pair = one Google Ads account / script
    """
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=64, unique=True)
    api_secret = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Mapping(models.Model):
    """
    One mapping can serve MULTIPLE campaigns
    """
    config_name = models.CharField(max_length=200, unique=True)

    # comma-separated campaign IDs
    campaign_ids = models.TextField(
    default="",
    help_text="Comma separated Google Ads campaign IDs"
)

    tracking_url = models.URLField()

    # multiple params to extract
    params = models.JSONField(default=list)

    last_suffix = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_campaign_id_list(self):
        return [c.strip() for c in self.campaign_ids.split(",") if c.strip()]

    def __str__(self):
        return self.config_name


class RunLog(models.Model):
    mapping = models.ForeignKey(Mapping, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    final_url = models.TextField(blank=True, null=True)
    extracted_value = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.mapping.config_name} @ {self.time}"
