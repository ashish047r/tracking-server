import asyncio
import json
from .fetcher import fetch_final_url, extract_params
from .utils import build_final_suffix
from .models import RunLog


def run_mapping(mapping):
    final_url = None
    extracted_map = None

    try:
        print("====== RUN_MAPPING START ======")
        print("CONFIG:", mapping.config_name)
        print("RAW PARAMS:", repr(mapping.params), type(mapping.params))
        print("TRACKING URL:", mapping.tracking_url)

        result = asyncio.run(fetch_final_url(mapping.tracking_url))
        final_url = result["final_url"]

        print("FINAL URL:", final_url)

        params = mapping.params

        if isinstance(params, str):
            params = params.strip()
            print("PARAM STRING AFTER STRIP:", repr(params))
            params = json.loads(params)

        print("PARAMS AFTER JSON LOAD:", params, type(params))

        if not isinstance(params, list):
            raise Exception("Params is not a list")

        extracted_map = extract_params(final_url, params)

        print("EXTRACTED MAP:", extracted_map)

        if not extracted_map:
            raise Exception("No params extracted")

        final_suffix = build_final_suffix(extracted_map)

        mapping.last_suffix = final_suffix
        mapping.save(update_fields=["last_suffix", "updated_at"])

        RunLog.objects.create(
            mapping=mapping,
            final_url=final_url,
            extracted_value=str(extracted_map),
            success=True,
        )

        print("SUCCESS — SUFFIX:", final_suffix)

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
