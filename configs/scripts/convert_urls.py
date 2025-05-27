#!/usr/bin/env python3
import json
import sys

"""Command line to run from smart_scraper : python ../configs/scripts/convert_urls.py outputs/urls_output.json outputs/converted_urls.json
"""

def convert_urls(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    urls = [item["detail_url"] for item in data if "detail_url" in item]
    output_data = {"base_urls": urls}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    print(f"Conversion finished. {len(urls)} URL(s) recorded in '{output_file}'.")

if __name__ == '__main__':
    convert_urls(sys.argv[1], sys.argv[2])
