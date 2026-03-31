"""
Online catalog lookup - searches vendor websites for product details by catalog number.
Falls back gracefully if no internet or no results.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import re

router = APIRouter(prefix="/api/catalog-online", tags=["Online Catalog"])

# Try importing requests - may not be available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from app.database import get_db
from app.auth import get_current_user
from app.models import User


def clean_text(text):
    """Strip HTML tags and extra whitespace."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def search_thermofisher(catalog_number):
    """Search Thermo Fisher Scientific."""
    try:
        url = f"https://www.thermofisher.com/search/results?query={catalog_number}&focusarea=Search+All"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            text = r.text
            # Try to find product name from title or meta
            title_match = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
            if title_match:
                title = clean_text(title_match.group(1))
                if catalog_number.lower() in title.lower() or "thermo" not in title.lower():
                    # Look for price
                    price_match = re.search(r'\$\s*([\d,]+\.?\d*)', text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else None
                    # Clean up title
                    name = title.split(' - ')[0].split(' | ')[0].strip()
                    if name and len(name) > 3 and name != "Search Results":
                        return {
                            "name": name,
                            "vendor": "Thermo Fisher Scientific",
                            "unit_price": price,
                            "catalog_number": catalog_number,
                        }
    except Exception:
        pass
    return None


def search_sigmaaldrich(catalog_number):
    """Search Sigma-Aldrich / MilliporeSigma."""
    try:
        url = f"https://www.sigmaaldrich.com/US/en/search/{catalog_number}?focus=products&page=1&perpage=5"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            text = r.text
            title_match = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
            if title_match:
                title = clean_text(title_match.group(1))
                name = title.split(' - ')[0].split(' | ')[0].strip()
                if name and len(name) > 3 and "search" not in name.lower():
                    price_match = re.search(r'\$\s*([\d,]+\.?\d*)', text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else None
                    return {
                        "name": name,
                        "vendor": "Sigma-Aldrich",
                        "unit_price": price,
                        "catalog_number": catalog_number,
                    }
    except Exception:
        pass
    return None


def search_generic(catalog_number):
    """Generic search using DuckDuckGo lite for product info."""
    try:
        url = f"https://lite.duckduckgo.com/lite/?q={catalog_number}+antibody+OR+reagent+catalog+price"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            text = r.text
            # Extract snippets - look for product-like results
            snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>([^<]+)</td>', text)
            links = re.findall(r'<td[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*class="result-link"[^>]*>([^<]+)</a>', text, re.DOTALL)

            vendor = None
            name = None
            price = None

            # Check link titles for product names
            for link_url, link_text in links[:5]:
                lt = clean_text(link_text)
                if catalog_number.lower() in lt.lower() or catalog_number.upper() in lt:
                    name = lt.split(' - ')[0].split(' | ')[0].strip()
                    # Detect vendor from URL
                    if "thermofisher" in link_url:
                        vendor = "Thermo Fisher Scientific"
                    elif "sigma" in link_url or "millipore" in link_url:
                        vendor = "Sigma-Aldrich"
                    elif "cellsignal" in link_url:
                        vendor = "Cell Signaling Technology"
                    elif "biolegend" in link_url:
                        vendor = "BioLegend"
                    elif "neb.com" in link_url or "nebiolabs" in link_url:
                        vendor = "New England Biolabs"
                    elif "abcam" in link_url:
                        vendor = "Abcam"
                    elif "bio-rad" in link_url:
                        vendor = "Bio-Rad"
                    elif "atcc" in link_url:
                        vendor = "ATCC"
                    elif "promega" in link_url:
                        vendor = "Promega"
                    elif "novus" in link_url:
                        vendor = "Novus Biologicals"
                    elif "santacruz" in link_url:
                        vendor = "Santa Cruz Biotechnology"
                    elif "invitrogen" in link_url:
                        vendor = "Invitrogen"
                    break

            # Check snippets for price
            for snippet in snippets[:5]:
                price_match = re.search(r'\$\s*([\d,]+\.?\d*)', snippet)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
                    break

            if name and len(name) > 3:
                return {
                    "name": name,
                    "vendor": vendor or "Unknown",
                    "unit_price": price,
                    "catalog_number": catalog_number,
                }
    except Exception:
        pass
    return None


@router.get("/{catalog_number}")
def lookup_online(
    catalog_number: str,
    current_user: User = Depends(get_current_user),
):
    """
    Search online for product details by catalog number.
    Tries multiple vendor sites and falls back to generic search.
    """
    if not HAS_REQUESTS:
        return {"found": False, "message": "Online lookup not available (requests library missing)"}

    # Try vendors in order
    for search_fn in [search_thermofisher, search_sigmaaldrich, search_generic]:
        result = search_fn(catalog_number)
        if result:
            return {
                "found": True,
                "name": result.get("name", ""),
                "vendor": result.get("vendor", ""),
                "unit_price": result.get("unit_price"),
                "inventory_type": guess_type(result.get("name", "")),
                "storage_temp": guess_storage(result.get("name", "")),
                "catalog_number": catalog_number,
                "source": "online",
            }

    return {"found": False, "message": f"No results found online for '{catalog_number}'"}


def guess_type(name):
    """Guess inventory type from product name."""
    name_lower = name.lower()
    if any(w in name_lower for w in ["antibody", "anti-", "igg", "igm"]):
        return "Antibody"
    if any(w in name_lower for w in ["competent", "bl21", "dh5", "bacteria", "e. coli"]):
        return "Bacterial Stock"
    if any(w in name_lower for w in ["cell line", "hepg2", "hela", "hek293"]):
        return "Cell Line"
    if any(w in name_lower for w in ["plasmid", "vector", "pgem", "pgl"]):
        return "Plasmid"
    if any(w in name_lower for w in ["primer", "oligo"]):
        return "Oligo"
    if any(w in name_lower for w in ["ecori", "bamhi", "restriction", "enzyme", "ligase", "polymerase"]):
        return "Assay Kit"
    if any(w in name_lower for w in ["dmem", "rpmi", "medium", "media", "serum", "fbs"]):
        return "Culture Medium"
    if any(w in name_lower for w in ["kit", "assay"]):
        return "Assay Kit"
    return "Chemical"


def guess_storage(name):
    """Guess storage temperature from product name."""
    name_lower = name.lower()
    if any(w in name_lower for w in ["competent", "bacteria"]):
        return "-80 deg C"
    if any(w in name_lower for w in ["cell line"]):
        return "-196 deg C (LN2)"
    if any(w in name_lower for w in ["antibody", "anti-", "enzyme", "restriction"]):
        return "-20 deg C"
    if any(w in name_lower for w in ["medium", "media", "serum"]):
        return "-20 deg C"
    return "4 deg C"
