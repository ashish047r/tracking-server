from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Mapping, ScriptAuth
from .services import run_mapping


# ---------------------------------------------------------
# Google Ads Script endpoint (GET)
# ---------------------------------------------------------
@csrf_exempt
def get_suffix(request):
    try:
        # ---- allow only GET ----
        if request.method != "GET":
            return JsonResponse(
                {"success": False, "error": "Invalid method"},
                status=405
            )

        # ---- auth headers ----
        api_key = request.headers.get("X-API-KEY")
        api_secret = request.headers.get("X-API-SECRET")

        if not api_key or not api_secret:
            return JsonResponse(
                {"success": False, "error": "Missing auth headers"},
                status=401
            )

        auth = ScriptAuth.objects.filter(
            api_key=api_key,
            api_secret=api_secret,
            is_active=True
        ).first()

        if not auth:
            return JsonResponse(
                {"success": False, "error": "Invalid API credentials"},
                status=403
            )

        # ---- params ----
        config_name = request.GET.get("config")
        campaign_id = request.GET.get("campaign_id")

        if not config_name or not campaign_id:
            return JsonResponse(
                {"success": False, "error": "Missing config or campaign_id"},
                status=400
            )

        mapping = Mapping.objects.filter(config_name=config_name).first()
        if not mapping:
            return JsonResponse(
                {"success": False, "error": "Config not found"},
                status=404
            )

        if not mapping.campaign_ids:
            return JsonResponse(
                {"success": False, "error": "No campaigns mapped"},
                status=200
            )

        campaign_ids = [
            c.strip() for c in mapping.campaign_ids.split(",") if c.strip()
        ]

        if str(campaign_id) not in campaign_ids:
            return JsonResponse(
                {"success": False, "error": "Campaign not mapped"},
                status=200
            )

        if not mapping.last_suffix:
            return JsonResponse(
                {"success": False, "error": "Suffix not ready"},
                status=200
            )

        # ---- SUCCESS ----
        return JsonResponse({
            "success": True,
            "final_suffix": mapping.last_suffix
        })

    except Exception as e:
        # 🔒 NEVER allow HTML traceback to reach Google Ads
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=200
        )


# ---------------------------------------------------------
# Backend runner endpoint (POST)
# ---------------------------------------------------------
@api_view(["POST"])
def run_single(request):
    config_name = request.data.get("config_name")

    if not config_name:
        return Response(
            {"success": False, "error": "config_name required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mapping = Mapping.objects.get(config_name=config_name)
        run_mapping(mapping)
        return Response({"success": True})
    except Mapping.DoesNotExist:
        return Response(
            {"success": False, "error": "Config not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
