"""Helpful function for the agent to make requests."""
import requests


def get(url):
    """Reads request text into memory."""
    r = requests.get(url)
    return r.text


def post(url, data):
    """Reads request text into memory."""
    r = requests.post(url, data=data)
    return r.text
