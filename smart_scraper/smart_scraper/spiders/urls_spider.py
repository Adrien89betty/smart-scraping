import scrapy
import random
from scrapy_playwright.page import PageMethod

class UrlsSpider(scrapy.Spider):
    name = "urls_spider"
    # *=========*/URL of the product list page to scrape/*=========*
    start_urls = ["https://www.championstore.com/fr_fr/outlet/outlet-femmes?_gl=1*18gy3jd*_up*MQ..*_ga*MjAzMjE3ODY0Mi4xNzQ1ODUxNjc0*_ga_QFNR51ZT9B*MTc0NTg1MTY3NC4xLjEuMTc0NTg1MTY5NS4wLjAuNzkzOTE2MTM3"]
    # *============================================================*

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "FEED_EXPORT_FIELDS": ["detail_url"],
    }

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

    def start_requests(self):
        self.logger.info(f"Spider starts with {len(self.start_urls)} URL(s)")

        for url in self.start_urls:
            headers = {
                "User-Agent": self.get_random_user_agent(),
                "Accept-Language": "fr-FR,fr;q=0.9",
            }
            self.logger.info(f"Sending the request : {url}")
            self.logger.info(f"User-Agent used : {headers['User-Agent']}")

            # JavaScript script to scroll to the bottom of the page
            auto_scroll_js = """
            async () => {
                let previousHeight = 0;
                let currentHeight = document.body.scrollHeight;
                while (currentHeight > previousHeight) {
                    window.scrollTo(0, currentHeight);
                    // Wait for 3 seconds after each scroll to ensure that products are loaded.
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    previousHeight = currentHeight;
                    currentHeight = document.body.scrollHeight;
                }
                console.log("Auto-scrolling terminé");
            }
            """

            page_methods = [PageMethod("evaluate", auto_scroll_js)]

            yield scrapy.Request(
                url=url,
                headers=headers,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": page_methods,
                },
                callback=self.parse,
                errback=self.handle_error
            )

    def parse(self, response):
        self.logger.info(f"Page processing: {response.url}")
        if response.status in [403, 429]:
            self.logger.warning(f"Acces denied ({response.status}) - Anti-bot protection detected.")
            return
        if response.status != 200:
            self.logger.error(f"HTTP error {response.status} on {response.url}")
            return
        if hasattr(self, "debug_mode") and self.debug_mode:
            self.logger.debug(f"HTML sample : \n{response.text[:1000]}")

        # Extracting product detail URLs from product cards.
        # *==================*/ADAPT SELECTOR HERE/*===================*
        # detail_urls = response.css(".product-tile__link::attr(href)").getall()
        detail_urls =  response.xpath("//li[contains(@class, 'product-item')]/a/@href").getall()
        # *============================================================*
        self.logger.info("URLs trouvées : %s", detail_urls)
        detail_urls = [response.urljoin(url) for url in detail_urls]
        unique_urls = list(set(detail_urls))
        for url in unique_urls:
            yield {"detail_url": url}

        # Handle pagination: if a 'next page' button is present.
        # -------------------*/Adapt selector here/*-------------------
        next_button = response.css('')
        # *============================================================*
        if next_button:
            self.logger.info("Pagination button found. Clicking to load next page...")
            yield scrapy.Request(
                url=response.url,
                dont_filter=True,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("click", 'button[aria-label="Aller à la page suivante"]'),
                        PageMethod("wait_for_timeout", 3000)
                    ],
                },
                callback=self.parse,
                errback=self.handle_error
            )
        else:
            self.logger.info("No pagination button found.")

        # Handle pagination: if a 'next page' anchor link is present.
        # -------------------*/Adapt selector here/*-------------------
        next_page = response.css('').get()
        # *============================================================*
        if next_page:
            next_page = response.urljoin(next_page)
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, callback=self.parse)
        else:
            self.logger.info("No next page found.")

    def handle_error(self, failure):
        self.logger.error(repr(failure))
