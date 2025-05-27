# import scrapy
# from scrapy_playwright.page import PageMethod

# class TestSpider(scrapy.Spider):
#     name = "test"
#     start_urls = ["https://www.uniqlo.com/fr/fr/products/E467504-000/01?colorDisplayCode=30&sizeDisplayCode=004"]

#     def start_requests(self):
#         for url in self.start_urls:
#             yield scrapy.Request(
#                 url,
#                 meta={
#                     "playwright": True,
#                     "playwright_include_page": True,
#                     "playwright_page_methods": [
#                         # Progressive scroll
#                         PageMethod("evaluate", "window.scrollBy(0, window.innerHeight / 2)"),
#                         PageMethod("wait_for_timeout", 1000),
#                         PageMethod("evaluate", "window.scrollBy(0, window.innerHeight)"),
#                         PageMethod("wait_for_timeout", 1000),
#                         PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
#                         PageMethod("wait_for_timeout", 2000),

#                         # Move mouse
#                         PageMethod("mouse.move", 300, 500),
#                         PageMethod("wait_for_timeout", 500),
#                         PageMethod("mouse.move", 500, 300),
#                         PageMethod("wait_for_timeout", 500),

#                         # Waiting for the page to be loaded
#                         PageMethod("wait_for_timeout", 3000),
#                     ],
#                 },
#                 callback=self.parse
#             )

#     async def parse(self, response):
#         self.logger.info("Page scraped successfuly !")

#         brand_name = response.css("span.brand-name::text").get(default="UNIQLO")
#         brand_url = response.css("a.brand-url::attr(href)").get(default=response.url)
#         currency = response.css("span.currency::text").get(default="EUR")
#         discount_percentage = response.css(".discount::text").get(default="0%")

#         try:
#             discount_price = float(response.css("p.fr-ec-price-text::text").get().replace("€", "").strip())
#         except (TypeError, ValueError, AttributeError):
#             discount_price = 0.0

#         gender = response.css("span.gender-label::text").get(default="Unisex")
#         offer_image_url = response.css("img.product-image::attr(src)").get(default="")

#         try:
#             offer_price = float(response.css("div.fr-ec-price__original-price::text").get().replace("€", "").strip())
#         except (TypeError, ValueError, AttributeError):
#             offer_price = 0.0

#         offer_url = response.url
#         product_description = response.css("div.productLongDescription-content::text").get(default="Description not available")
#         product_name = response.css("h1.fr-ec-display::text").get(default="Name not available")
#         tags = response.css("ul.tags-list li::text").getall()
#         vendor_icon_url = response.css("img.vendor-icon::attr(src)").get(default="")
#         vendor_name = response.css("span.vendor-name::text").get(default="UNIQLO")
#         vendor_url = response.css("a.vendor-url::attr(href)").get(default=response.url)

#         yield {
#             "brand_name": brand_name,
#             "brand_url": brand_url,
#             "currency": currency,
#             "discount_percentage": discount_percentage,
#             "discount_price": discount_price,
#             "gender": gender,
#             "offer_image_url": offer_image_url,
#             "offer_price": offer_price,
#             "offer_url": offer_url,
#             "product_description": product_description,
#             "product_name": product_name,
#             "tags": tags,
#             "vendor_icon_url": vendor_icon_url,
#             "vendor_name": vendor_name,
#             "vendor_url": vendor_url,
#         }
