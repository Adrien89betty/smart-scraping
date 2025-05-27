# IDSide Scraper
IDSide Scraper is a modular web scraping project built with [Scrapy](https://docs.scrapy.org/en/latest/) and [Scrapy-Playwright](https://github.com/scrapy-plugins/scrapy-playwright). It is designed to extract product data from e-commerce websites and is configurable via JSON files validated with [Pydantic](https://docs.pydantic.dev/latest/). It consists of a main spider that extracts detailed product data and an auxiliary spider that extracts product details URLs from a products collection page. In addition, a utility script is provided to convert JSON objects from the spider's output into a Python List of URLs suitable for the JSON config files.

## Table of Contents
- #### [Main features](#main-features-1)

- #### [Project Structure](#project-structure-1)

- #### [Installation](#installation-1)

- #### [Configuration file overview](#configuration-file-overview-1)

- #### [Command lines](#command-lines-1)

    - #### [Running the Main Spider](#running-the-main-spider-1)

    - #### [Running the URLs Spider](#running-the-urls-spider-1)

    - #### [Converting JSON objects](#converting-json-objects-1)

    - #### [Scrapy console](#scrapy-console-1)

- #### [Quick start tutorial](#quick-start-tutorial-1)

- #### [Troubleshooting](#troubleshooting-1)




## Main features
* **Modular Configuration:** Use JSON configuration files (e.g. `idside-scraping/configs/config_example.json`) that are validated with `Pydantic`.

* **Main spider:** The main scraper entry point. The `MainSpider` is the spider intended for scraping products datas. It is 'self-configurable' via the JSON configuration files.

* **Dynamic Data Extraction:** Extract product details such as name, prices, descriptions, and images.

* **Multiple ways to extract datas:** The scraper supports and uses several elements and technics for data extraction *(e.g. `CSS` and `Xpath` selectors, `meta` tags or `JSON-LD`)*.

* **Playwright Integration:** Use `Playwright` for JavaScript rendering and dynamic interactions with pages.

* **Utility spider:** A dedicated spider (`idside-scraping/idside_scraper/idside_scraper/spiders/urls_spider.py`) to extract product details URLs from products collections pages.

* **Conversion Utility:** A script (`idside-scraping/configs/scripts/convert_urls.py`) that converts a list of JSON objects into a simple urls list that can be easily copied into a JSON configuration file (`"base_urls": [<url>, <url>, <url>,...]`).

* **Customizable:** Easily update selectors and settings via configuration files without touching the code.



## Project Structure
```bash
idside-scraping/
├── configs/                       # JSON config files and utility scripts
│   ├── scripts/
│   │   └── convert_urls.py
│   ├── config_brand.json
│   ├── config_anotherbrand.json
│   ├── config_anotherbrand.json
│   └── … (config_columbia.json, config_jonak.json, etc.)
├── idside_scraper/                # Scrapy project
│   ├── idside_scraper/
│   │   ├── __init__.py
│   │   ├── items.py               # models, loader and helpers
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   ├── settings.py            # settings Scrapy & Playwright
│   │   ├── spiders/               # parsing and fetching
│   │   │   ├── __init__.py
│   │   │   ├── main_spider.py     # products details scraping
│   │   │   ├── urls_spider.py     # products URLs fetching
│   │   │   └── test_spider.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── config_loader.py   # loads/validates JSON via Pydantic
│   │       └── jsonld_getter.py   # extraction/completion via JSON-LD
│   ├── outputs/                   # JSON export files (ignore by Git)
│   │     ├── brand_output.json
│   │     ├── anotherbrand_output.json
│   │     └── … (columbia_output.json, jonak_output.json, etc.)
│   └── scrapy.cfg
│
├── virtual_env/                   # Python virtual env (ignore by Git)
├── .gitignore
├── README.md
└──requirements.txt               # Python dependencies


```



## Installation
Clone the repository:
```bash
git clone git@github.com:idside-eu/idside-scraping.git
```

Create and activate a Python virtual environment:
```bash
python3 -m venv venv_name
source venv_name/bin/activate
```
Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```



## Configuration file overview
The project uses JSON configuration files (`idside-scraping/configs/config_example.json`) that define:

* **Base URLs:** A list of product details page URLs to scrape.

* **Selectors:** `CSS` or `Xpath` selectors for extracting product data (e.g., `product_name`, `offer_price`, `offer_image_url`).

* **Pagination settings** (if applicable).

* **Anti-bot settings:** For Playwright human behavior usage.

* **Scroll settings:** To simulate user scrolls on dynamic pages.

* **Headers:** Default headers for requests (e.g., `Accept-Language`, `Referer`).

An example configuration file structure (`config_columbia.json`) look like:

```json
{
  "base_urls": [
      "https://www.columbiasportswear.fr/FR/p/chaussure-de-randonnee-mid-peakfreak-ii-outdry-femme-2100091.html?dwvar_2100091_color=010",
      "https://www.columbiasportswear.fr/FR/p/pantalon-de-ski-impermeable-cirque-bowl-femme-602-m-r-195981024753.html?dwvar_195981024753_color=602",
      "https://www.columbiasportswear.fr/FR/p/bonnet-pompon-a-maille-torsadee-boundless-days-unisexe-2092641.html?dwvar_2092641_color=581",
      "https://www.columbiasportswear.fr/FR/p/chaussure-de-randonnee-facet-75-ii-outdry-femme-2100121.html?dwvar_2100121_color=466",
      "https://www.columbiasportswear.fr/FR/p/gants-de-ski-impermeables-powbound-femme-2097051.html?dwvar_2097051_color=602",
      "https://www.columbiasportswear.fr/FR/p/veste-en-duvet-a-capuche-harmony-falls-femme-2085372.html?dwvar_2085372_color=609"
  ],
  "brand_name": "Columbia",
  "brand_url": "https://www.columbiasportswear.fr/",
  "vendor_name": "Columbia",
  "vendor_url": "https://www.columbiasportswear.fr/",
  "currency": "EUR",
  "gender": "",
  "selectors": {
    "product_name": "",
    "offer_price": "//div[contains(@class, 'price')]//span[contains(@class, 'strike-through')]//span[@itemprop='price']/text()",
    "offer_image_url": "//div[contains(@class, 'product-gallery')]//li[contains(@class, 'swiper-slide')]//img/@src",
    "discount_price": "//div[contains(@class, 'price')]//span[contains(@class, 'sales')]//span[@itemprop='price']/text()",
    "discount_percentage": "",
    "product_description": "",
    "vendor_icon_url": "",
    "tags": ""
  },
  "pagination": {
    "enabled": false,
    "selector": ""
  },
  "anti_bot": {
    "use_playwright": true,
    "delay": 5
  },
  "scroll": {
    "enabled": true,
    "times": 3,
    "delay": 2
  },
  "headers": {
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.columbiasportswear.fr/FR/c/bonnes-affaires-femme?icpa=grid&icid=hdrbn&icsa=ALL&prid=mwkf&icst=visnav&crid=women&icca=btn"
  },
  "debug_mode": true
}
```
***Note :*** *It is important that you keep the exact same structure when you duplicate JSON configuration files, otherwise* `pydantic` *will raise errors ! If you want to change it for your needs, you'll have to update* `config_loader.py`*,* `items.py` *and* `main_spider.py` *accordingly*.



## Command lines
### Running the Main Spider
The main spider (MainSpider) extracts detailed product data. To run it from terminal, use (from inside `idside_scraper` dir, if you are at the root, it wont works):

```bash
scrapy crawl main_spider -a config_file=config_name.json -o outputs/name_output.json
```

### Running the URLs Spider
The auxiliary `urls_spider.py` extracts product details URLs from a products collection page. It is useful to easily fill or update `base_urls` field in your configuration files.

```bash
scrapy crawl urls_spider -o outputs/urls_output.json
```
### Converting JSON objects
Use the `convert_urls.py` script to transform the JSON output from `urls_spider.py` into a "list of URLs" suitable for the JSON config files. From inside `idside_scraper` dir, run:

```bash
python ../configs/scripts/convert_urls.py outputs/urls_output.json outputs/converted_urls.json
```
*This script reads `idside-scraping/idside_scraper/outputs/urls_output.json` file with objects containing* `detail_url` *and creates a new JSON file* (`idside-scraping/idside_scraper/outputs/converted_urls.json`) *with a single object that has a* `base_urls` *key containing a list of URLs.*

### Scrapy console
```bash
scrapy shell <url>
```
*Can be useful to see how your selectors works before running MainSpider !*




## Quick start tutorial

Follow these steps to perform a scrape on a brand’s website (here, “Columbia”).

### 1. Looking for JSON-LD
1. Open the brand’s website in your browser.
2. Open DevTools and look in the **HTML** for a `<script type="application/ld+json">` containing `"@type": "Product"`.
3. If found, note which properties are available (`name`, `description`, `image`, `offers.price`, etc.). You can use these as a fallback extraction source.

### 2. Analyze the HTML for your selectors
1. Inspect the DOM (via DevTools) to locate your key data points:
   - `offer_price` (standard or crossed-out price)
   - `discount_price` (sale price)
   - `product_name`
   - `product_description`
   - `offer_image_url`
2. You can test your CSS or XPath selectors in the Scrapy shell console:
   ```bash
   scrapy shell "https://…/example-product"
   # CSS example
   response.css("span.price-current::text").get()
   # XPath example
   response.xpath("//span[@class='current']/text()").get()
   ```

### 3. Create and set a new configuration file
1. In `idside-scraping/configs/`, create a new JSON file (e.g. `config_columbia.json`).

2. Open your `config_columbia.json` and adjust fields values (cf. [Set config file](#set-config-file)):

- base_urls
- selectors (product_name, offer_price, etc.)
- fixed values (brand_url, currency, gender, …)

### 4. Run the MainSpider
Run this command to test extraction on a few URLs *(replace 'name' for the real brand name.)*:
```bash
scrapy crawl main_spider -a config_file=config_name.json -o outputs/name_output.json
```
You’ll get a JSON output file (in `idside-scraping/idside_scraper/outputs/`) file with partial or complete data extracts. Ajust settings if it necessary.

### 5. Generate the product URLs list
Open `idside-scraping/idside_scraper/idside_scraper/spiders/urls_spider.py` and replace `start_urls`value with your desired page URL:
```python
# *=========*/URL of the product list page to scrape/*=========*
start_urls = ["https://www.columbia.com/fr_fr/outlet/outlet-femmes?"]
# *============================================================*
```

Update the selector (CSS or XPath) that targets the \<a href="…"> links:
```python
# Extracting product detail URLs from product cards.
# *==================*/ADAPT SELECTOR HERE/*===================*
# detail_urls = response.css(".product-tile__link::attr(href)").getall()
detail_urls =  response.xpath("//div[contains(@class, 'product-item')]/a/@href").getall()
# *============================================================*
```

Run:
```bash
scrapy crawl urls_spider -o outputs/urls_output.json
```
You'll get mutiple JSON objects in `idside-scraping/idside_scraper/outputs/urls_output.json` listing all individual product pages URLs.

### 6. Convert the JSON objects to a simple URL list
run:
```bash
python ../configs/scripts/convert_urls.py outputs/urls_output.json outputs/converted_urls.json
```
This outputs in `idside-scraping/idside_scraper/outputs/converted_urls.json`, a simple list of URLs to copy in your JSON config file.

### 7. Update your JSON config file and rerun
1. Paste the extracted URLs into the "start_urls" field of your config file. (e.g.`config_columbia.json`).

2. (Optional) tweak any other selectors or defaults.

3. Rerun MainSpider and if everything goes well, you’ll have a complete set of product data !



## Set config file
Generaly speaking, it is possible to leave a field as "blank" without raising any errors. To do so, just leave it with an empty string `""`.

### Fixed values
```json
  "base_urls": [
      "https://www.columbiasportswear.fr/FR/p/chaussure-de-randonnee-mid-peakfreak-ii-outdry-femme-2100091.html?dwvar_2100091_color=010",
      "https://www.columbiasportswear.fr/FR/p/pantalon-de-ski-impermeable-cirque-bowl-femme-602-m-r-195981024753.html?dwvar_195981024753_color=602",
      "https://www.columbiasportswear.fr/FR/p/bonnet-pompon-a-maille-torsadee-boundless-days-unisexe-2092641.html?dwvar_2092641_color=581",
      "https://www.columbiasportswear.fr/FR/p/chaussure-de-randonnee-facet-75-ii-outdry-femme-2100121.html?dwvar_2100121_color=466",
      "https://www.columbiasportswear.fr/FR/p/gants-de-ski-impermeables-powbound-femme-2097051.html?dwvar_2097051_color=602",
      "https://www.columbiasportswear.fr/FR/p/veste-en-duvet-a-capuche-harmony-falls-femme-2085372.html?dwvar_2085372_color=609"
  ],
  ```
  `base_urls` accepts a list of strings. It should always be a list even with only one unique URL.

  ```json
  "brand_name": "Columbia",
  "brand_url": "https://www.columbiasportswear.fr/",
  "vendor_name": "Columbia",
  "vendor_url": "https://www.columbiasportswear.fr/",
  "currency": "EUR",
  ```
  Fields filled with basic informations (Common name, home page URL, ...)

  ```json
  "gender": "",
  ```
  Leave it as empty (like this) only if you can see in the `Referer` URL *(see below)* a word that could indicates the gender *(e.g. 'men', 'mens', 'women', 'womans', ...)*.
  Otherwise, and only if you know exactly what kind of products data you are about to scrap, you'll have to fill it with `Female`, `Male` or `Unisex`. like this :
  ```json
  "gender": "Female",
  ```

  ### Selectors
  ```json
  "selectors": {
    "product_name": "",
    "offer_price": "//div[contains(@class, 'price')]//span[contains(@class, 'strike-through')]//span[@itemprop='price']/text()",
    "offer_image_url": "//div[contains(@class, 'product-gallery')]//li[contains(@class, 'swiper-slide')]//img/@src",
    "discount_price": "//div[contains(@class, 'price')]//span[contains(@class, 'sales')]//span[@itemprop='price']/text()",
    "discount_percentage": "",
    "product_description": "",
    "vendor_icon_url": "",
    "tags": ""
  },
  ```
  Here it is possible to use either CSS or Xpath selectors (see [Scrapy doc](https://docs.scrapy.org/en/latest/topics/selectors.html)). Fields whose value can be retrieved via JSON-LD *(if any)* do not need to be filled in, so leave an empty string instead `""`
  Leave `discount_percentage` empty as well because it will be computed on the fly.
  Same for `vendor_icon_url` who will be processed later.
  *(Note that* `vendor_icon_url` *will be* `Null` *if no image is found and* `tags` *will return an empty list* `[]` *if set like this. It's allowed.)*

  ### Playwright interactions an delays
  ```bash
  "pagination": {
    "enabled": false,
    "selector": ""
  },
  "anti_bot": {
    "use_playwright": true,
    "delay": 5
  },
  "scroll": {
    "enabled": true,
    "times": 3,
    "delay": 2
  },
  ```
  `pagination` is set to `false` because the targets are product details pages, so we'll find all the informations needed on one single page.
  `anti-bot` and `scroll` has to be set to `true` all the time.

  ### Headers
  ```bash
  "headers": {
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.columbiasportswear.fr/FR/c/bonnes-affaires-femme?icpa=grid&icid=hdrbn&icsa=ALL&prid=mwkf&icst=visnav&crid=women&icca=btn"
  },
  ```
  `Accepted-language` has to be set like this.
  `Referer` is typically filled in with a products collection page URL *(this same URL will be used in UrlsSpider to get all product details pages URLs.)*.

  ```bash
  "debug_mode": true
  ```
  Leave as `true` for complete logging.


## Troubleshooting
**Dynamic Content Not Loaded:** If you notice that not all products are being scraped, increase the scroll delay in your configuration (scroll.delay) or adjust the number of scroll iterations (scroll.times).

**User-Agent Issues:** If you encounter issues with being blocked, try updating the list of User-Agents in the `get_random_user_agent()` function (in `config_loader.py`).

**Playwright Errors:** Ensure that Playwright is correctly installed and that you have run playwright install to download the required browsers.

**Configuration Errors:** If the configuration file fails validation, check the JSON syntax and ensure that all required fields are present.

**0 items stored in output JSON:** There is a validation at the end of `main_spider.py` who sytematically skip items if they contains one or more fields with a default value *(no datas extracted)* If so, it is possible that you get nothing in output. This is probably because one value is missing so try comment the final part of the parse() function in `main_spider.py` to see the recordings and figure out what fields are involved.
