import scrapy
import json
import os
from scrapy.loader import ItemLoader
from smart_scraper.items import ProductItem, ProductLoader
from smart_scraper.items import compute_discount_percentage
from itemloaders.processors import MapCompose
from scrapy_playwright.page import PageMethod
from smart_scraper.utils.config_loader import load_config
from smart_scraper.utils.jsonld_getter import extract_jsonld_data
from smart_scraper.utils.jsonld_getter import check_for_default_value
from smart_scraper.utils.jsonld_getter import fetch_jsonld_data

class MainSpider(scrapy.Spider):
    name = "main_spider"

    def __init__(self, config_file, *args, **kwargs):
        super(MainSpider, self).__init__(*args, **kwargs)

        # Load JSON config
        self.config = load_config(config_file)
        self.logger.info(f"Config json file loaded : {self.config}")
        self.start_urls = [str(url) for url in self.config.base_urls]

        #Fetch fixed values.
        self.brand_url = self.config.brand_url or None
        self.vendor_url = self.config.vendor_url or None
        self.vendor_name = self.config.vendor_name or None
        self.currency = self.config.currency or None
        self.gender = self.config.gender or None

        # Fetch selectors
        self.product_name_selector = self.config.selectors.product_name
        self.offer_price_selector = self.config.selectors.offer_price
        self.offer_image_url_selector = self.config.selectors.offer_image_url

        self.discount_price_selector = self.config.selectors.discount_price or None
        self.discount_percentage_selector = self.config.selectors.discount_percentage or None
        self.product_description_selector = self.config.selectors.product_description or None
        self.vendor_icon_url_selector = self.config.selectors.vendor_icon_url or None
        self.tags_selector = self.config.selectors.tags or None

        self.brand_name_selector = self.config.selectors.brand_name if hasattr(self.config.selectors, "brand_name") else None
        self.brand_name = self.config.brand_name if hasattr(self.config, "brand_name") else None

        # Fetch pagination settings
        self.pagination_enabled = self.config.pagination.enabled or False
        self.pagination_selector = self.config.pagination.selector or None

        # Fetch playwright settings
        self.use_playwright = self.config.anti_bot.use_playwright or False
        self.delay = self.config.anti_bot.delay or 0

        # Fetch scroll settings
        self.scroll_enabled = self.config.scroll.enabled or False
        self.scroll_times = self.config.scroll.times or 3
        self.scroll_delay = self.config.scroll.delay or 2

        # Add debug mode with a default value
        self.debug_mode = self.config.debug_mode if hasattr(self.config, "debug_mode") else False
        self.logger.info("Spider __init__ completed.")

    def start_requests(self):
        """Starts requests with headers and Playwright if enabled."""
        self.logger.info(f"Spider starts with {len(self.start_urls)} URL(s)")

        for url in self.start_urls:
            # Get a random user-agent
            headers = {
                "User-Agent": self.config.headers.get_random_user_agent(),
                "Accept-Language": self.config.headers.Accept_Language or "fr-FR,fr;q=0.9",
                "Referer": self.config.headers.Referer or None,
            }

            self.logger.info(f"Sending the request : {url}")
            self.logger.info(f"User-Agent used : {headers['User-Agent']}")

            request_params = {
                "url": url,
                "callback": self.parse,
                "errback": self.handle_error,  # error handler
                "headers": headers,
            }

            # Adding Playwright mode if enabled
            if self.use_playwright:
                self.logger.info(f"Playwright activated with a delay of {self.delay} sec.")

                request_params["meta"] = {
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_timeout", self.delay * 1000)
                    ],

                }

                # Adding Scroll if enabled
                if self.scroll_enabled:
                    for _ in range(self.scroll_times):
                        request_params["meta"]["playwright_page_methods"].append(
                            PageMethod(
                                "evaluate",
                                "window.scrollTo(0, document.body.scrollHeight)",
                            )
                        )
                        request_params["meta"]["playwright_page_methods"].append(
                            PageMethod("wait_for_timeout", self.scroll_delay * 1000)
                        )

            yield scrapy.Request(**request_params)

    def handle_error(self, failure):
        """Log errors during requests."""
        self.logger.error(f"Error during query : {failure.request.url}")
        self.logger.error(f"Error details : {repr(failure)}")

        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            self.logger.error(f"HTTP error {response.status} on {response.url}")

        elif failure.check(scrapy.downloadermiddlewares.retry.RetryMiddleware):
            self.logger.warning(f"Attempt to retry for {failure.request.url}")

        elif failure.check(scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware):
            self.logger.warning(f"Proxy problem {failure.request.url}")


    def parse(self, response):
        """Extracting data based on selectors defined in the config using ProductLoader."""
        self.logger.info(f"Page processing: {response.url}")
        if response.status in [403, 429]:
            self.logger.warning(f"Acces denied ({response.status}) - Anti-bot protection detected.")
            return
        if response.status != 200:
            self.logger.error(f"HTTP error {response.status} on {response.url}")
            return
        if hasattr(self, "debug_mode") and self.debug_mode:
            self.logger.debug(f"HTML sample : \n{response.text[:1000]}")


        loader = ProductLoader(item=ProductItem(), response=response)

        # Checks the selector type (css ou Xpath).
        def is_xpath(selector):
            xpath_patterns = ("/", ".//", "./")
            sel =  selector.strip()
            for p in xpath_patterns:
                if sel.startswith(p):
                    return True
            return False


        # Extracts the value of a selector (supports css or Xpath).
        def safe_add(field_name, selector):
            if selector:
                if is_xpath(selector):
                    loader.add_xpath(field_name, selector)
                    extracted = loader.get_output_value(field_name)
                    self.logger.debug(f"Xpath - Extracted value for {field_name}: {extracted}")
                else:
                    loader.add_css(field_name, selector)
                    extracted = loader.get_output_value(field_name)
                    self.logger.debug(f"CSS - Extracted value for {field_name}: {extracted}")


        # For 'brand_name': Uses the selector if defined, otherwise the fixed value (defined in items.py)
        if self.brand_name_selector:
            safe_add("brand_name", self.brand_name_selector)
        elif self.brand_name:
            loader.add_value("brand_name", self.brand_name)

        # We check if we can get the percentage with a selector, otherwise we'll compute it once all items loaded.
        if self.discount_percentage_selector:
            safe_add("discount_percentage", self.discount_percentage_selector)

        # For other fields extracted by selectors
        safe_add("product_name", self.product_name_selector)
        safe_add("offer_price", self.offer_price_selector)
        safe_add("discount_price", self.discount_price_selector)
        safe_add("product_description", self.product_description_selector)
        safe_add("tags", self.tags_selector)

        # For fields with fixed values
        loader.add_value("brand_url", self.brand_url)
        loader.add_value("currency", self.currency)
        loader.add_value("vendor_name", self.vendor_name)
        loader.add_value("vendor_url", self.vendor_url)

        # For fields requiring processing via MapCompose
        if self.offer_image_url_selector:
            if is_xpath(self.offer_image_url_selector):
                loader.add_xpath("offer_image_url", self.offer_image_url_selector,
                        MapCompose(lambda x: response.urljoin(x)))
            else:
                loader.add_css("offer_image_url", self.offer_image_url_selector,
                            MapCompose(lambda x: response.urljoin(x)))
        else:
            loader.add_value("offer_image_url", "No image available")

        if self.vendor_icon_url_selector:
            loader.add_css("vendor_icon_url", self.vendor_icon_url_selector,
                        MapCompose(lambda x: response.urljoin(x)))
        else:
            # If vendor_url is set, vendor_url + "/favicon.ico" is used to get favicon
            if self.vendor_url:
                loader.add_value("vendor_icon_url", f"{self.vendor_url.rstrip('/')}/favicon.ico")

        loader.add_value("offer_url", response.url)

        # Checks if hard value has been passed to "gender" in JSON config, otherwise, process it in items.py.
        if self.gender:
            loader.add_value("gender", self.gender)
        else:
            loader.add_value("gender", self.config.headers.Referer)

        item = loader.load_item()

        # Compute discount_percentage
        if self.discount_percentage_selector is None:
            computed = compute_discount_percentage(item.get("offer_price"), item.get("discount_price"))
            item["discount_percentage"] = computed


        # =================== FETCH JSON‑LD ========================
        missing_val = check_for_default_value(item)
        jsonld_data = extract_jsonld_data(response)

        if missing_val and jsonld_data:
            item = fetch_jsonld_data(jsonld_data, item)
        # ==========================================================


        """Filtering incomplete products before yield."""
        # Defines the fields and their default values ​​to check (excluding vendor_icon_url and tags).
        # =================== TO DEBUG, COMMENT THIS SECTION ========================
        required_fields = {
            "brand_name": "Unknown brand",
            "brand_url": "Unknown brand URL",
            "currency": "Unknown currency",
            "discount_percentage": "No discount",
            "discount_price": "No discount",
            "gender": "Unspecified",
            "offer_image_url": "No image available",
            "offer_price": "Price not available",
            "offer_url": "No URL available",
            "product_description": "Description not found",
            "product_name": "Product name not found",
            "vendor_name": "Unknown vendor",
            "vendor_url": "Unknown vendor URL",
        }

        complete = True
        for field, default in required_fields.items():
            value = item.get(field)
            if isinstance(default, list):
                if not value or value == default:
                    complete = False
                    self.logger.debug(f"Field '{field}' is incomplete (value: {value})")
                    break
            elif isinstance(default, str):
                if isinstance(value, str):
                    if not value or value.strip() == default:
                        complete = False
                        self.logger.debug(f"Field '{field}' is incomplete (value: '{value}')")
                        break
                else:
                    if not value or str(value).strip() == default:
                        complete = False
                        self.logger.debug(f"Field '{field}' is incomplete (value: {value})")
                        break
            else:
                if value == default:
                    complete = False
                    self.logger.debug(f"Field '{field}' is incomplete (value: {value})")
                    break

        if complete:
            self.logger.info("Item is complete. Yielding item.")
            self.logger.info(f"Product's data extracted: {item}")
            yield item
        else:
            self.logger.info("Incomplete item skipped.")
        # ===========================================================================
        # --------------------AND UNCOMMENT THIS ONE---------------------------------
        # self.logger.info(f"Product's data extracted: {item}")
        # yield item
        # ---------------------------------------------------------------------------


        # Pagination if enabled
        if self.pagination_enabled:
            next_page = response.css(self.pagination_selector).get()
            if next_page:
                self.logger.info(f"Following pagination to: {next_page}")
                yield response.follow(next_page, callback=self.parse, headers=self.headers)
