import asyncio
import json
from django.utils import timezone

from .fetcher import fetch_final_url, extract_params
from .utils import build_final_suffix, extract_full_query
from .models import RunLog


def run_mapping(mapping):
    final_url = None
    extracted_map = None

    now = timezone.now()

    # =====================================================
    # 🔒 MILLIS-BASED GATING (CORE SAFETY LOGIC)
    # =====================================================
    if mapping.window_ms > 0 and mapping.frequency > 0:
        interval_ms = mapping.window_ms / mapping.frequency

        if mapping.last_run_at:
            elapsed_ms = (now - mapping.last_run_at).total_seconds() * 1000

            if elapsed_ms < interval_ms:
                # Too early → do nothing safely
                return

    try:
        result = asyncio.run(fetch_final_url(mapping.tracking_url))
        final_url = result["final_url"]

        # =====================================================
        # PARAM EXTRACTION
        # =====================================================
        if mapping.extract_all_params:
            final_suffix = extract_full_query(final_url)
            extracted_value = final_suffix
        else:
            params = mapping.params
            if isinstance(params, str):
                params = json.loads(params)

            extracted_map = extract_params(final_url, params)
            if not extracted_map:
                raise Exception("No params extracted")

            final_suffix = build_final_suffix(extracted_map)
            extracted_value = str(extracted_map)

        # =====================================================
        # SAVE
        # =====================================================
        mapping.last_suffix = final_suffix
        mapping.last_run_at = now
        mapping.save(update_fields=["last_suffix", "last_run_at", "updated_at"])

        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=extracted_value,
            success=True,
        )

    except Exception as e:
        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=str(extracted_map),
            success=False,
            error_message=str(e),
        )
        raise



# -----------------------------------------------------
# 🔥 BURST MODE — NO GATING (FOR CLIENT REQUIREMENT)
# -----------------------------------------------------
def generate_suffix_burst(mapping):
    """
    Generates suffix WITHOUT any time gating.
    Intended for burst / high-frequency runs.
    """
    final_url = None
    extracted_map = None

    try:
        result = asyncio.run(fetch_final_url(mapping.tracking_url))
        final_url = result["final_url"]

        if mapping.extract_all_params:
            final_suffix = extract_full_query(final_url)
            extracted_value = final_suffix
        else:
            params = mapping.params
            if isinstance(params, str):
                params = json.loads(params)

            extracted_map = extract_params(final_url, params)
            if not extracted_map:
                raise Exception("No params extracted")

            final_suffix = build_final_suffix(extracted_map)
            extracted_value = str(extracted_map)

        mapping.last_suffix = final_suffix
        mapping.last_run_at = timezone.now()
        mapping.save(update_fields=["last_suffix", "last_run_at", "updated_at"])

        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=extracted_value,
            success=True,
        )

    except Exception as e:
        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=str(extracted_map),
            success=False,
            error_message=str(e),
        )
        raise
