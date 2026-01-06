from google.ads.googleads.client import GoogleAdsClient
from django.conf import settings
import os

def get_google_ads_client(login_customer_id: str | None = None):
    """
    Creates Google Ads API client using env vars
    """

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }

    # if login_customer_id:
    #     config["login_customer_id"] = login_customer_id.replace("-", "")

    return GoogleAdsClient.load_from_dict(config)
