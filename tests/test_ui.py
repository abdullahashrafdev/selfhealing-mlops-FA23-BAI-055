"""
tests/test_ui.py
Selenium headless Chrome test for the Sentiment Analyzer frontend.
Uses the three fixed element IDs: text-input, submit-btn, result-output.
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,800")

    drv = webdriver.Chrome(options=chrome_options)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()


def test_frontend_sentiment(driver):
    """
    Loads the frontend, submits a sentence via the UI,
    and asserts the result-output is non-empty and contains
    POSITIVE, NEGATIVE, or Confidence.
    """
    driver.get(f"{BASE_URL}/")

    wait = WebDriverWait(driver, 15)

    # Send a test sentence to the text-input field
    text_input = wait.until(EC.presence_of_element_located((By.ID, "text-input")))
    test_sentence = "The food was absolutely delicious and the chef clearly has exceptional skill"
    text_input.clear()
    text_input.send_keys(test_sentence)

    # Click the submit button
    submit_btn = driver.find_element(By.ID, "submit-btn")
    submit_btn.click()

    # Wait for result-output to be populated
    result_output = wait.until(
        EC.text_to_be_present_in_element((By.ID, "result-output"), "")
    )

    # Give the async fetch a moment to complete
    time.sleep(3)

    result_element = driver.find_element(By.ID, "result-output")
    result_text = result_element.text.strip()

    assert result_text != "", "result-output is empty after clicking submit"

    assert any(keyword in result_text for keyword in ("POSITIVE", "NEGATIVE", "Confidence")), \
        f"result-output does not contain expected content. Got: '{result_text}'"
