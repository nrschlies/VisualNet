"""
@package data_scraping.web_scraper
@brief Provides web scraping functionalities.

This module contains classes and functions for web scraping, including
fetching web pages and parsing HTML content.

@class WebScraper
@brief A class for web scraping.
@date 2024-07-01
@license MIT
@dependencies
- BeautifulSoup (bs4) - MIT License
- requests - Apache License 2.0
- urllib - Python Software Foundation License
- json - Python Software Foundation License
"""
"""
@package data_scraping.web_scraper
@brief Provides web scraping functionalities.

This module contains classes and functions for web scraping, including
fetching web pages, handling headers and cookies, and parsing HTML content.

@class WebScraper
@brief A class for web scraping.
@date 2024-07-01
@license MIT
@dependencies
- BeautifulSoup (bs4) - MIT License
- requests - Apache License 2.0
- urllib - Python Software Foundation License
- json - Python Software Foundation License
"""

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import json

class WebScraper:
    def __init__(self, base_url, headers=None, cookies=None, user_agent='WebScraperBot'):
        self.base_url = base_url
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.user_agent = user_agent
        self.robot_parser = self._initialize_robot_parser()

    def _initialize_robot_parser(self):
        parsed_url = urlparse(self.base_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        robot_parser = RobotFileParser()
        robot_parser.set_url(robots_url)
        robot_parser.read()
        return robot_parser

    def _is_allowed_by_robots(self, url):
        return self.robot_parser.can_fetch(self.user_agent, url)

    def fetch_page(self, url, params=None, method='GET'):
        full_url = urljoin(self.base_url, url)
        if not self._is_allowed_by_robots(full_url):
            raise PermissionError(f"Fetching the URL '{full_url}' is disallowed by the site's robots.txt file.")
        
        if method == 'GET':
            response = requests.get(full_url, headers=self.headers, cookies=self.cookies, params=params)
        elif method == 'POST':
            response = requests.post(full_url, headers=self.headers, cookies=self.cookies, data=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.text

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def scrape_data(self, url, parser_func, params=None, method='GET'):
        html = self.fetch_page(url, params=params, method=method)
        soup = self.parse_html(html)
        return parser_func(soup)

    def extract_links(self, soup, css_selector='a'):
        links = [a.get('href') for a in soup.select(css_selector) if a.get('href')]
        return links

    def extract_text(self, soup, css_selector):
        texts = [element.get_text(strip=True) for element in soup.select(css_selector)]
        return texts

    def extract_metadata(self, soup):
        metadata = {}
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata[meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                metadata[meta['property']] = meta.get('content', '')
        return metadata

    def extract_table(self, soup, css_selector='table'):
        table = soup.select_one(css_selector)
        if not table:
            return []
        
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        rows = []
        for tr in table.find_all('tr')[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows

    def handle_pagination(self, url, parser_func, params=None, method='GET', next_page_selector='a.next'):
        all_data = []
        while url:
            html = self.fetch_page(url, params=params, method=method)
            soup = self.parse_html(html)
            data = parser_func(soup)
            all_data.extend(data)
            
            next_page = soup.select_one(next_page_selector)
            if next_page and next_page.get('href'):
                url = urljoin(self.base_url, next_page['href'])
            else:
                break
        return all_data

    def extract_headings(self, soup):
        headings = {}
        for level in range(1, 7):
            tag = f'h{level}'
            headings[tag] = [h.get_text(strip=True) for h in soup.find_all(tag)]
        return headings

    def extract_paragraphs(self, soup):
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        return paragraphs

    def extract_lists(self, soup, css_selector='ul, ol'):
        lists = []
        for list_element in soup.select(css_selector):
            items = [li.get_text(strip=True) for li in list_element.find_all('li')]
            lists.append(items)
        return lists

    def extract_images(self, soup, css_selector='img'):
        images = [img.get('src') for img in soup.select(css_selector) if img.get('src')]
        return images

    def extract_json_ld(self, soup):
        json_ld_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_data = json.loads(script.string)
                json_ld_data.append(json_data)
            except json.JSONDecodeError:
                continue
        return json_ld_data

    def extract_forms(self, soup, css_selector='form'):
        forms = []
        for form in soup.select(css_selector):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method', 'get').lower(),
                'fields': {}
            }
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                name = input_tag.get('name')
                if name:
                    form_data['fields'][name] = input_tag.get('value', '')
            forms.append(form_data)
        return forms
