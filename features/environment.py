"""
Environment for Behave Testing
"""

from os import getenv
import requests
from selenium import webdriver

WAIT_SECONDS = int(getenv("WAIT_SECONDS", "30"))
BASE_URL = getenv("BASE_URL", "http://localhost:8080")
DRIVER = getenv("DRIVER", "chrome").lower()


def before_all(context):
    """Executed once before all tests"""
    context.wait_seconds = WAIT_SECONDS
    context.base_url = BASE_URL

    # Select either Chrome or Firefox
    if "firefox" in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.wait_seconds)
    context.driver.set_window_size(1280, 1300)
    context.config.setup_logging()
    delete_all_customers(context)


def after_scenario(context, scenario):  # pylint: disable=unused-argument
    """Executed after each scenario, whether it passed or failed"""
    delete_all_customers(context)


def after_all(context):
    """Executed once after all tests"""
    context.driver.quit()


def delete_all_customers(context):
    """Deletes every customer in the database behind BASE_URL"""
    resp = requests.get(f"{context.base_url}/customers", timeout=context.wait_seconds)
    assert resp.status_code == 200, "Could not list customers"
    for customer in resp.json():
        resp = requests.delete(
            f"{context.base_url}/customers/{customer['id']}",
            timeout=context.wait_seconds,
        )
        assert resp.status_code == 204, f"Could not delete customer {customer['id']}"


######################################################################
# Utility functions to create web drivers
######################################################################


def get_chrome():
    """Creates a headless Chrome driver"""
    print("Running Behave using the Chrome driver...\n")
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    print("Running Behave using the Firefox driver...\n")
    options = webdriver.FirefoxOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
