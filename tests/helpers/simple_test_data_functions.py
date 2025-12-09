"""
This page contains functions for creating simple
(i.e., primitive data type) test data
"""
import uuid

from tests.helpers.counter import next_int


def generate_test_urls(count: int) -> list[str]:
    results = []
    for i in range(count):
        url = f"example.com/{uuid.uuid4().hex}"
        results.append(url)

    return results


def generate_test_url(i: int) -> str:
    return f"test.com/{i}"

def generate_test_name(i: int | None = None) -> str:
    if i is None:
        return f"Test Name {next_int()}"
    return f"Test Name {i}"

def generate_test_description(i: int) -> str:
    return f"Test description {i}"

def generate_test_html(i: int) -> str:
    return f"<html><body><h1>Test {i}</h1></body></html>"