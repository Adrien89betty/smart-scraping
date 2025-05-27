import json
import requests
from smart_scraper.items import clean_html_tags, clean_text
from urllib.parse import urljoin
from requests.exceptions import RequestException


# Fetch all <script type="application/ld+json"> tags
def extract_jsonld_data(response):
    """
    Extract Product JSON-LD data from a response.
    It looks for <script type="application/ld+json"> tags and returns the first valid
    JSON object (or one from a list) that represents a Product.

    :param response: Scrapy Response object.
    :return: dict containing the Product data if found, otherwise an empty dict.
    """
    scripts = response.css('script[type="application/ld+json"]::text').getall()
    for script in scripts:
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue

        # If data is a dictionnary, checks for his type
        if isinstance(data, dict):
            if data.get('@type', '').lower() == 'product':
                return data
        # If data is a list
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('@type', '').lower() == 'product':
                    return item
    return {}


# Checks for some fields, if they contain the default or a retrieved value.
def check_for_default_value(item):
    fields = {
            "discount_price": "No discount",
            "offer_image_url": "No image available",
            "offer_price": "Price not available",
            "product_description": "Description not found",
            "product_name": "Product name not found",
        }
    empty_fields = False

    for field, default in fields.items():
            value = item.get(field)
            if isinstance(default, list):
                if not value or value == default:
                    empty_fields = True
                    break
            elif isinstance(default, str):
                if isinstance(value, str):
                    if not value or value.strip() == default:
                        empty_fields = True
                        break
                else:
                    if not value or str(value).strip() == default:
                        empty_fields = True
                        break
            else:
                if value == default:
                    empty_fields = True
                    break
    return empty_fields


# Checks that a URL returns an image.
def is_image(url: str, timeout: int = 5) -> bool:
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        return resp.status_code == 200
    except RequestException:
        return False


def fetch_jsonld_data(jsonld_data, item):
    """If the product description could not be retrieved or is empty, attempt to retrieve it from JSON-LD."""
    # =================== DUPLICATE THIS BLOCK IF ANOTHER FIELD NEEDS TO BE PROCESSED ========================
    if not item.get("product_description") or item.get("product_description") == "Description not found":
        desc = jsonld_data.get("description")
        if desc:
            item["product_description"] = clean_text(clean_html_tags(desc))
    # ==========================================================

    if not item.get("offer_image_url") or item["offer_image_url"] == "No image available":
        imgs = jsonld_data.get("image")

        # Conversion to list to avoid unexpected behaviors.
        if not imgs:
            imgs_list = []
        elif isinstance(imgs, str):
            imgs_list = [imgs]
        else:
            imgs_list = list(imgs)

        valid_images = []
        if imgs:
            for raw_path in imgs_list:
                # Rebuild url if relative.
                full_url = raw_path if raw_path.startswith(("http://", "https://")) else urljoin(item.get("brand_url",""), raw_path)
                if is_image(full_url):
                    valid_images.append(full_url)
            if valid_images:
                item["offer_image_url"] = valid_images

    if not item.get("product_name") or item.get("product_name") == "Product name not found":
        name = jsonld_data.get("name")
        if name:
            item["product_name"] = clean_text(clean_html_tags(name))

    return item
