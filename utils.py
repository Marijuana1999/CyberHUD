# utils.py
import re

def extract_params(url):
    if "?" not in url:
        return []
    query = url.split("?", 1)[1]
    return query.split("&")
