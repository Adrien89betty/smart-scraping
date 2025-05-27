# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import requests
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst, Identity, Compose
from bs4 import BeautifulSoup
from html import unescape


class ProductItem(scrapy.Item):
    brand_name = scrapy.Field(default="Unknown brand")
    brand_url = scrapy.Field(default="Unknown brand URL")
    currency = scrapy.Field(default="Unknown currency")
    discount_percentage = scrapy.Field(default="No discount")
    discount_price = scrapy.Field(default="No discount")
    gender = scrapy.Field(default="Unspecified")
    offer_image_url = scrapy.Field(default="No image available")
    offer_price = scrapy.Field(default="Price not available")
    offer_url = scrapy.Field(default="No URL available")
    product_description = scrapy.Field(default="Description not found")
    product_name = scrapy.Field(default="Product name not found")
    tags = scrapy.Field(default=[])
    vendor_icon_url = scrapy.Field()
    vendor_name = scrapy.Field(default="Unknown vendor")
    vendor_url = scrapy.Field(default="Unknown vendor URL")

# Clean and converts prices, percentages to float.
def clean_price_discount(value):
    if not value:
        return None
    signs = ("%", "€", "EUR", "-")
    value = value.replace(",", ".")
    for s in signs:
        value = value.replace(s, "")
    try:
        return float(value.strip())
    except ValueError:
        return None

# Compute discount percentage if not displayed on the website.
def compute_discount_percentage(offer_price, discount_price):
    try:
        op = float(offer_price)
        dp = float(discount_price)
        if op > 0:
            percentage = round((1 - dp / op) * 100, 1)
            return percentage
        else:
            return "No discount"
    except (TypeError, ValueError):
        return "No discount"

# Removes spaces from strings (begining - end)
def clean_text(value):
    if value:
        return value.strip()
    return None

# Returns an empty list if value is None.
def ensure_list(value):
    if value:
        return [value]
    return []

# Returns the default value if no value.
def default_if_empty(value, default):
    if value not in (None, '', []):
        return value
    else:
        return default

# Find keywords in url to determine the gender.
def find_gender(str_val):
    url = str_val.lower()
    if url.startswith("http"):
        key_words = (
            "femme",
            "femmes",
            "women",
            "womens",
            "woman",
            "homme",
            "hommes",
            "men",
            "mens",
            "man"
        )
        for idx, word in enumerate(key_words):
            if word in url:
                if idx <= 4:
                    return "Female"
                else:
                    return "Male"
        return "Unspecified"
    return str_val

# Checks if url is valid and provides an image.
def verify_vendor_icon(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return url
        else:
            return None
    except Exception:
        return None

# Ensure that a field contains only urls.
def filter_valid_urls(value):
    if value and (value.startswith("http://") or value.startswith("https://")):
        return value
    return None

# Removes any duplicates urls.
def remove_duplicates(urls):
    clean_urls = []
    for url in urls:
        if url not in clean_urls:
            clean_urls.append(url)
    return clean_urls

# Remove any html tags if still present in text.
def clean_html_tags(value):
    if value:
        value = unescape(unescape(value))
        soup = BeautifulSoup(value, "html.parser")
        text = soup.get_text(separator=" ")
        return " ".join(text.split())
    return value


class ProductLoader(ItemLoader):
    default_output_processor = TakeFirst()

    brand_name_in = MapCompose(clean_text)
    brand_url_in = MapCompose(clean_text)
    currency_in = MapCompose(clean_text)
    discount_percentage_in = MapCompose(clean_price_discount)
    discount_price_in = MapCompose(clean_price_discount)
    gender_in = MapCompose(clean_text, find_gender)
    offer_image_url_in = MapCompose(clean_text, filter_valid_urls)
    offer_image_url_out = Compose(remove_duplicates)
    offer_price_in = MapCompose(clean_price_discount)
    offer_url_in = MapCompose(clean_text)
    product_description_in = MapCompose(clean_html_tags, clean_text)
    product_name_in = MapCompose(clean_text)
    tags_in = MapCompose(clean_text, ensure_list)
    tags_out = Identity()
    vendor_icon_url_in = MapCompose(clean_text, verify_vendor_icon)
    vendor_name_in = MapCompose(clean_text)
    vendor_url_in = MapCompose(clean_text)


    # Overloads load_item() to ensure that default values are used if neccessary.
    def load_item(self):
        item = super().load_item()

        for field in item.fields:
            default_value = item.fields[field].get('default')
            item[field] = default_if_empty(item.get(field), default_value)
        return item
