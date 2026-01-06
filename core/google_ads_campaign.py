from google.ads.googleads.errors import GoogleAdsException
from .google_ads_client import get_google_ads_client


def update_campaign_tracking_template(
    *,
    login_customer_id: str,
    customer_id: str,
    campaign_id: str,
    final_suffix: str,
):
    client = get_google_ads_client(login_customer_id)

    campaign_service = client.get_service("CampaignService")

    customer_id = customer_id.replace("-", "")
    campaign_id = str(campaign_id)

    operation = client.get_type("CampaignOperation")
    campaign = operation.update

    campaign.resource_name = campaign_service.campaign_path(
        customer_id, campaign_id
    )

    


    # 🔑 THIS IS THE FIELD THAT ACTUALLY WORKS
    campaign.tracking_url_template = "{lpurl}?" + final_suffix
    operation.update_mask.paths.append("tracking_url_template")

    try:
        response = campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[operation],
        )
        return {"success": True}

    except GoogleAdsException as ex:
        return {
            "success": False,
            "errors": [e.message for e in ex.failure.errors],
        }


