import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
SELENIUM_URL = os.environ.get("SELENIUM_URL", "http://localhost:4444/wd/hub")

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,800")

    drv = webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=chrome_options
    )
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()

def test_frontend_sentiment(driver):
    driver.get(f"{BASE_URL}/")
    wait = WebDriverWait(driver, 15)
    text_input = wait.until(EC.presence_of_element_located((By.ID, "text-input")))
    text_input.clear()
    text_input.send_keys("The food was absolutely delicious and the chef clearly has exceptional skill")
    submit_btn = driver.find_element(By.ID, "submit-btn")
    submit_btn.click()
    time.sleep(3)
    result_element = driver.find_element(By.ID, "result-output")
    result_text = result_element.text.strip()
    assert result_text != "", "result-output is empty after clicking submit"
    assert any(keyword in result_text for keyword in ("POSITIVE", "NEGATIVE", "Confidence")), \
        f"result-output does not contain expected content. Got: '{result_text}'"
