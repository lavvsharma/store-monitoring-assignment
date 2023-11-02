"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

import requests


def retry_if_connection_error(exception: Exception):
    """
        Return True when there is a ConnectionError i.e. the URL is not accessible
    """
    is_connection_error = isinstance(exception, requests.exceptions.RequestException)

    if is_connection_error:
        return True
