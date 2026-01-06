import asyncio
import json
from .fetcher import fetch_final_url, extract_params
from .utils import build_final_suffix, extract_full_query
from .models import RunLog


def run_mapping(mapping):
    final_url = None
    extracted_map = None

    try:
        print("====== RUN_MAPPING START ======")
        print("CONFIG:", mapping.config_name)
        print("TRACKING URL:", mapping.tracking_url)
        print("EXTRACT ALL PARAMS:", mapping.extract_all_params)

        result = asyncio.run(fetch_final_url(mapping.tracking_url))
        final_url = result["final_url"]

        print("FINAL URL:", final_url)

        # =====================================================
        # 🔥 CASE 1: Extract ALL params
        # =====================================================
        if mapping.extract_all_params:
            final_suffix = extract_full_query(final_url)

            if not final_suffix:
                raise Exception("No query params found in final URL")

            extracted_value = final_suffix

        # =====================================================
        # 🔒 CASE 2: Extract SELECTED params (existing behavior)
        # =====================================================
        else:
            params = mapping.params
            print("RAW PARAMS:", repr(params), type(params))

            if isinstance(params, str):
                params = json.loads(params)

            if not isinstance(params, list):
                raise Exception("Params must be a list")

            extracted_map = extract_params(final_url, params)

            print("EXTRACTED MAP:", extracted_map)

            if not extracted_map:
                raise Exception("No params extracted")

            final_suffix = build_final_suffix(extracted_map)
            extracted_value = str(extracted_map)

        # =====================================================
        # SAVE
        # =====================================================
        mapping.last_suffix = final_suffix
        mapping.save(update_fields=["last_suffix", "updated_at"])

        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=extracted_value,
            success=True,
        )

        print("SUCCESS — FINAL SUFFIX:", final_suffix)

    except Exception as e:
        print("ERROR:", str(e))

        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=str(extracted_map),
            success=False,
            error_message=str(e),
        )
        raise
