import os
import json
import random
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Dict, List, Optional

# Defines validation models with Pydantic
class HeadersConfig(BaseModel):
    Accept_Language: Optional[str] = "fr-FR,fr;q=0.9"
    Referer: Optional[str] = None

    def get_random_user_agent(self):
        """Returns a random User-Agent for each query."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/100.0.1185.39",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36",
            "Mozilla/5.0 (Android 11; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0",
            "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.36.109 Chrome/99.0.4844.51 Safari/537.36"
        ]
        return random.choice(user_agents)

class ScrollConfig(BaseModel):
    enabled: bool = False
    times: int = 3
    delay: int = 2

class PaginationConfig(BaseModel):
    enabled: bool
    selector: Optional[str]

class AntiBotConfig(BaseModel):
    use_playwright: bool
    delay: int

class SelectorsConfig(BaseModel):
    product_name: str
    offer_price: str
    offer_image_url: str
    discount_price: Optional[str] = None
    discount_percentage: Optional[str] = None
    product_description: Optional[str] = None
    vendor_icon_url: Optional[str] = None
    tags: Optional[str] = None

class ScraperConfig(BaseModel):
    base_urls: List[HttpUrl]
    brand_name: Optional[str] = None
    brand_url: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_url: Optional[str] = None
    currency: Optional[str] = "EUR"
    gender: Optional[str] = None
    selectors: SelectorsConfig
    pagination: Optional[PaginationConfig] = None
    anti_bot: Optional[AntiBotConfig] = None
    headers: Optional[HeadersConfig] = None
    scroll: Optional[ScrollConfig] = None


# JSON validation and load function
def load_config(json_filename):
    """Loads and validates a configuration JSON file."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../configs"))
    json_path = os.path.join(base_dir, json_filename)

    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return ScraperConfig(**data)  # Automatic validation with Pydantic
    except Exception as e:
        raise ValueError(f"file validation error. {json_filename}: {e}")

# validation test
# if __name__ == "__main__":
#     try:
#         config = load_config("config_bonobo.json")
#         print("Valid configuration !", config)
#     except Exception as e:
#         print(f"Validation error : {e}")
