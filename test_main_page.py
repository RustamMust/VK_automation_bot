from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from main_page_2 import VKPage


def test_authorization_page(browser):
    """Функция для авторизации на сайте vk.com и открытия чата"""
    email_tab = browser.find_element(By.XPATH, '//*[@id="index_email"]')
    email_tab.send_keys('Логин')
    email_tab.send_keys(Keys.RETURN)
    time.sleep(2)
    password_input = browser.find_element(By.NAME, "password")
    password_input.send_keys("Пароль")
    password_input.send_keys(Keys.RETURN)
    time.sleep(3)
    community_button = browser.find_element(By.CSS_SELECTOR, "li#l_gr a.LeftMenuItem-module__item--XMcN9")
    community_button.click()
    time.sleep(2)
    browser.get('https://vk.com/club224120400')
    time.sleep(3)
    chat_button = browser.find_element(By.XPATH, '//*[@class="group_name"]')
    chat_button.click()
    time.sleep(3)


def test_main_game(browser):
    vk_page = VKPage(browser)
    vk_page.parse_chat_until_word_start(browser)

