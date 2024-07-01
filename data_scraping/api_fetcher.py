"""
@package data_scraping.api_fetcher
@brief Provides API fetching functionalities.

This module contains classes and functions for fetching data from APIs,
including support for various HTTP methods and pagination handling.

@class APIFetcher
@brief A class for fetching data from APIs.
@date 2024-07-01
@license MIT
@dependencies
- requests - Apache License 2.0
"""

import requests

class APIFetcher:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers or {}

    def fetch_data(self, endpoint, params=None, method='GET', data=None, json=None):
        url = f"{self.base_url}/{endpoint}"
        response = self._make_request(url, params=params, method=method, data=data, json=json)
        return response.json()

    def fetch_paginated_data(self, endpoint, params=None, method='GET', data=None, json=None, next_page_param='page', start_page=1):
        all_data = []
        page = start_page

        while True:
            params = params or {}
            params[next_page_param] = page
            response = self._make_request(f"{self.base_url}/{endpoint}", params=params, method=method, data=data, json=json)
            json_data = response.json()
            all_data.extend(json_data)

            if 'next' not in response.links:
                break

            page += 1

        return all_data

    def _make_request(self, url, params=None, method='GET', data=None, json=None):
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, params=params, data=data, json=json)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, params=params, data=data, json=json)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            raise

    def fetch_headers(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self._make_request(url, params=params, method='HEAD')
        return response.headers

    def fetch_status_code(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self._make_request(url, params=params, method='GET')
        return response.status_code

    def fetch_data_with_retry(self, endpoint, params=None, method='GET', data=None, json=None, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                return self.fetch_data(endpoint, params=params, method=method, data=data, json=json)
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                attempt += 1
                if attempt == retries:
                    raise
