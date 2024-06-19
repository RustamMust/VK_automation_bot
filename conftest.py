from selenium import webdriver
import pytest
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope='session')
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Скрыть факт использования автоматизации
    chrome_browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    chrome_browser.implicitly_wait(10)
    chrome_browser.get('https://vk.com/')
    return chrome_browser

