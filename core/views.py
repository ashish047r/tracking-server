from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Mapping, ScriptAuth
from .services import run_mapping


@csrf_exempt
def get_suffix(request):
    try:
        if request.method != "GET":
            return JsonResponse({"success": False}, status=405)

        api_key = request.headers.get("X-API-KEY")
        api_secret = request.headers.get("X-API-SECRET")

        if not api_key or not api_secret:
            return JsonResponse({"success": False}, status=401)

        auth = ScriptAuth.objects.filter(
            api_key=api_key,
            api_secret=api_secret,
            is_active=True
        ).first()

        if not auth:
            return JsonResponse({"success": False}, status=403)

        config_name = request.GET.get("config")
        if not config_name:
            return JsonResponse({"success": False}, status=400)

        mapping = Mapping.objects.filter(config_name=config_name).first()
        if not mapping:
            return JsonResponse({"success": False}, status=404)

        run_mapping(mapping)

        if not mapping.last_suffix:
            return JsonResponse({"success": False}, status=200)

        return JsonResponse({
            "success": True,
            "final_suffix": mapping.last_suffix
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=200)
