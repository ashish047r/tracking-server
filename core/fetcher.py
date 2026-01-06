import httpx
from urllib.parse import urljoin, urlparse, parse_qs

MAX_HOPS = 10


# -------------------------------------------------------
# REDIRECT RESOLUTION (NO JS, NO PROXIES)
# -------------------------------------------------------

async def fetch_final_url(tracking_url: str) -> dict:
    """
    Follows redirects manually and returns the TRUE final URL
    (uses response.url, not the last requested URL).
    """
    visited = set()
    current_url = tracking_url
    hops = []

    async with httpx.AsyncClient(
        follow_redirects=False,
        timeout=15.0
    ) as client:

        for _ in range(MAX_HOPS):
            if current_url in visited:
                raise Exception("Redirect loop detected")

            visited.add(current_url)

            response = await client.get(
                current_url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "*/*"
                }
            )

            hops.append({
                "url": current_url,
                "status": response.status_code,
                "location": response.headers.get("location"),
            })

            # Handle HTTP redirects
            if 300 <= response.status_code < 400 and "location" in response.headers:
                current_url = urljoin(current_url, response.headers["location"])
                continue

            print("FINAL URL (BACKEND):", current_url)
            print("HOPS:")
            for h in hops:
                print(h)


            # ✅ FINAL URL — MUST USE response.url
            return {
                "final_url": str(response.url),
                "hops": hops
            }

        raise Exception("Too many redirects")


# -------------------------------------------------------
# MULTI-PARAM EXTRACTION
# -------------------------------------------------------

def extract_params(final_url: str, param_keys: list[str]) -> dict:
    """
    Extracts selected query params from final resolved URL.
    """
    parsed = urlparse(final_url)
    query = parse_qs(parsed.query)

    extracted = {}

    for key in param_keys:
        values = query.get(key)
        if values and values[0]:
            extracted[key] = values[0]

    return extracted
