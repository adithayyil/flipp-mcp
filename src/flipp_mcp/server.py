import json
import random
import re

import requests
from mcp.server.fastmcp import FastMCP


def _generate_sid():
    return random.randint(1000000000000000, 9999999999999999)


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
        "Accept": "*/*",
        "Referer": "https://flipp.com/",
        "Origin": "https://flipp.com",
    }


def _clean_postal(postal_code):
    return postal_code.replace(" ", "").upper()


def _fetch_flipp(postal_code, locale="en"):
    sid = _generate_sid()
    url = "https://dam.flippenterprise.net/api/flipp/data"
    params = {
        "locale": locale,
        "postal_code": _clean_postal(postal_code),
        "sid": sid,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_flyer_items(flyer_id, locale="en"):
    sid = _generate_sid()
    url = f"https://dam.flippenterprise.net/api/flipp/flyers/{flyer_id}/flyer_items"
    params = {
        "locale": locale,
        "sid": sid,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_flyer_item_detail(item_id, postal_code, locale="en"):
    sid = _generate_sid()
    url = f"https://dam.flippenterprise.net/api/flipp/flyer_items/{item_id}"
    params = {
        "locale": locale,
        "postal_code": _clean_postal(postal_code),
        "sid": sid,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_flyer_stores(flyer_id, postal_code, locale="en"):
    sid = _generate_sid()
    url = f"https://dam.flippenterprise.net/api/flipp/flyers/{flyer_id}/stores/nearby"
    params = {
        "locale": locale,
        "postal_code": _clean_postal(postal_code),
        "sid": sid,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_flyer_pages(flyer_id, locale="en"):
    sid = _generate_sid()
    url = f"https://dam.flippenterprise.net/api/flipp/flyers/{flyer_id}/flyer_pages"
    params = {
        "locale": locale,
        "sid": sid,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_loyalty_programs(postal_code, locale="en"):
    sid = _generate_sid()
    url = "https://dam.flippenterprise.net/api/flipp/loyalty_programs"
    params = {
        "locale": locale,
        "postal_code": _clean_postal(postal_code),
        "sid": sid,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_top_merchants(locale="en-ca"):
    url = f"https://flipp-com-apis.flippback.com/merchants/top/{locale}"
    response = requests.get(url, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


_SIZE_MULTI_RE = re.compile(
    r"(?P<count>\d+)\s*x\s*(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>g|kg|lb|oz|ml|mL|L)\b",
    re.IGNORECASE,
)
_SIZE_RE = re.compile(
    r"(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>g|kg|lb|oz|ml|mL|L)\b",
    re.IGNORECASE,
)


def _parse_size(name):
    multi = _SIZE_MULTI_RE.search(name)
    if multi:
        return (
            float(multi.group("count")) * float(multi.group("qty")),
            multi.group("unit").lower(),
        )
    single = _SIZE_RE.search(name)
    if single:
        return float(single.group("qty")), single.group("unit").lower()
    return None, None


def _to_base_unit(qty, unit):
    unit = unit.lower()
    if unit in ("g", "ml"):
        return qty / 1000, "kg" if unit == "g" else "L"
    if unit == "kg":
        return qty, "kg"
    if unit == "lb":
        return qty * 0.453592, "kg"
    if unit == "oz":
        return qty * 0.0283495, "kg"
    if unit == "l":
        return qty, "L"
    return None, None


def _search_flipp_items(postal_code, query, locale="en"):
    url = "https://backflipp.wishabi.com/flipp/items/search"
    params = {
        "postal_code": _clean_postal(postal_code),
        "q": query,
        "locale": locale,
    }
    response = requests.get(url, params=params, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def get_flipp_data(postal_code: str, locale: str = "en") -> str:
    """Fetch Flipp flyers and coupons for a postal code."""
    return json.dumps(_fetch_flipp(postal_code, locale))


def get_flipp_summary(postal_code: str, locale: str = "en") -> str:
    """Return a short summary of flyers and coupons for a postal code."""
    data = _fetch_flipp(postal_code, locale)
    return (
        f"flyers: {len(data.get('flyers', []))}\n"
        f"coupons: {len(data.get('coupons', []))}"
    )


def get_flyer_items(flyer_id: str, limit: int = 50, locale: str = "en") -> str:
    """Fetch itemized products and prices for a specific flyer."""
    items = _fetch_flyer_items(flyer_id, locale)
    if limit > 0:
        items = items[:limit]
    return json.dumps(items)


def get_flyer_item_detail(item_id: str, postal_code: str, locale: str = "en") -> str:
    """Fetch detailed info for a single flyer item."""
    return json.dumps(_fetch_flyer_item_detail(item_id, postal_code, locale))


def get_flyer_stores(flyer_id: str, postal_code: str, locale: str = "en") -> str:
    """Fetch nearby stores for a flyer."""
    return json.dumps(_fetch_flyer_stores(flyer_id, postal_code, locale))


def get_flyer_pages(flyer_id: str, locale: str = "en") -> str:
    """Fetch flyer page images and item positions."""
    return json.dumps(_fetch_flyer_pages(flyer_id, locale))


def get_loyalty_programs(postal_code: str, locale: str = "en") -> str:
    """Fetch available loyalty programs for a postal code."""
    return json.dumps(_fetch_loyalty_programs(postal_code, locale))


def get_top_merchants(locale: str = "en-ca") -> str:
    """Fetch the list of top merchants."""
    return json.dumps(_fetch_top_merchants(locale))


def get_merchant_flyer_items(
    postal_code: str,
    merchant: str,
    limit: int = 30,
    locale: str = "en",
) -> str:
    """Find a merchant's flyer and return its itemized sale items."""
    data = _fetch_flipp(postal_code, locale)
    flyers = data.get("flyers", [])
    query = merchant.lower()
    match = None
    for flyer in flyers:
        if query in flyer.get("merchant", "").lower():
            match = flyer
            break
    if match is None:
        return json.dumps({"error": f"no flyer found for {merchant!r}"})
    items = _fetch_flyer_items(match["id"], locale)
    if limit > 0:
        items = items[:limit]
    return json.dumps(
        {
            "flyer_id": match["id"],
            "merchant": match.get("merchant"),
            "valid_from": match.get("valid_from"),
            "valid_to": match.get("valid_to"),
            "count": len(items),
            "items": items,
        }
    )


def search_flipp_items(query: str, postal_code: str, limit: int = 20) -> str:
    """Search sale items across all flyers for a postal code, sorted by unit price."""
    data = _search_flipp_items(postal_code, query)
    raw = [i for i in data.get("items", []) if i.get("item_type") == "flyer"]

    results = []
    for item in raw:
        name = item.get("name") or ""
        current = item.get("current_price")
        qty, unit = _parse_size(name)
        base_qty, base_unit = _to_base_unit(qty, unit) if qty else (None, None)
        unit_price = None
        if base_qty and current is not None:
            unit_price = round(current / base_qty, 2)
        results.append(
            {
                "merchant_name": item.get("merchant_name"),
                "name": name,
                "current_price": current,
                "original_price": item.get("original_price"),
                "sale_story": item.get("sale_story"),
                "valid_from": item.get("valid_from"),
                "valid_to": item.get("valid_to"),
                "flyer_id": item.get("flyer_id"),
                "flyer_item_id": item.get("flyer_item_id"),
                "size_qty": qty,
                "size_unit": unit,
                "base_qty": base_qty,
                "base_unit": base_unit,
                "unit_price": unit_price,
                "unit_label": f"per {base_unit}" if base_unit else None,
                "image_url": item.get("clean_image_url") or item.get("image_url"),
            }
        )

    results.sort(
        key=lambda x: (
            x["unit_price"] is None,
            x["unit_price"] if x["unit_price"] is not None else float("inf"),
            x["current_price"] if x["current_price"] is not None else float("inf"),
        )
    )

    if limit > 0:
        results = results[:limit]

    return json.dumps(
        {
            "query": query,
            "postal_code": _clean_postal(postal_code),
            "total": len(raw),
            "returned": len(results),
            "items": results,
        }
    )


def create_mcp(host: str = "127.0.0.1", port: int = 8000):
    mcp = FastMCP("flipp", host=host, port=port)
    mcp.add_tool(get_flipp_data)
    mcp.add_tool(get_flipp_summary)
    mcp.add_tool(get_flyer_items)
    mcp.add_tool(get_flyer_item_detail)
    mcp.add_tool(get_flyer_stores)
    mcp.add_tool(get_flyer_pages)
    mcp.add_tool(get_loyalty_programs)
    mcp.add_tool(get_top_merchants)
    mcp.add_tool(get_merchant_flyer_items)
    mcp.add_tool(search_flipp_items)
    return mcp


def main():
    mcp = create_mcp()
    mcp.run()


if __name__ == "__main__":
    main()
