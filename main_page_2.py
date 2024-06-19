import re
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
import requests


def send_message(browser, message):
    """Функция, для отправки сообщения"""
    message_box = browser.find_element(By.CSS_SELECTOR, "div.im_editable.im-chat-input--text._im_text")
    message_box.send_keys(message)
    message_box.send_keys(Keys.RETURN)
    time.sleep(2)


def find_city_json() -> List[str]:
    """Функция формирует и возвращает список городов"""
    url = ('https://gist.githubusercontent.com/gorborukov/'
           '0722a93c35dfba96337b/raw/435b297ac6d90d13a68935e1ec7a69a225969e58/russia')
    response = requests.get(url)

    if response.status_code == 200:
        cities_data = response.json()
        cities_list = [city['city'] for city in cities_data]
        return cities_list


def choose_opponent(players):
    """Функция возвращает случайного пользователя из списка пользователей"""
    return random.choice(players)


def send_turn_message(browser, city, username):
    """Функция отправляет сообщение по шаблону Город {city}. @{username}, тебе на {player_city_letter}."""
    if city[-1].upper() in ['Ь', 'Ъ', 'Ы']:
        player_city_letter = city[-2].upper()
    else:
        player_city_letter = city[-1].upper()

    message = f"Город {city}. @{username}, тебе на {player_city_letter}."
    send_message(browser, message)


def player_out(browser, username):
    """Функция отправляет сообщение по шаблону Игрок @{username} выбывает."""
    message = f"Игрок @{username} выбывает."
    send_message(browser, message)
    time.sleep(2)


def get_online_players(browser) -> List[str]:
    """Функция формирует и возвращает список игроков"""
    chat_users_button = browser.find_element(By.XPATH, '//*[@class="_im_chat_members im-page--members"]')
    chat_users_button.click()
    time.sleep(2)

    participant_elements = browser.find_elements(By.XPATH, "//div[@class='Entity__aside']/a")
    href_values = [element.get_attribute("href") for element in participant_elements]

    href_values = href_values[2:]
    href_values.remove('https://vk.com/mustafaev_r')
    href_values = [href[15:] for href in href_values]
    print(f'Список с ID текущих игроков: {href_values}')

    chat_users_close_button = browser.find_element(By.XPATH, '//div[@data-testid="modal-close-button"]')
    chat_users_close_button.click()
    return href_values


class VKPage:
    my_player = '@mustafaev_r'
    players = []
    used_cities_in_game = []
    LAST_MESSAGE_LOCATOR = '//*[@class="im-mess-stack _im_mess_stack "][last()]//div[@class="im-mess--text wall_module _im_log_body"]'
    LAST_MESSAGE_PLAYER_NAME_LOCATOR = '//*[@class="im-mess-stack _im_mess_stack "][last()]//div[@class="im-mess-stack--pname"]/a'

    def __init__(self, browser):
        self.browser = browser
        self.players = get_online_players(browser)

    def parse_chat_until_word_start(self, browser):
        """Функция парсит чат до тех пор, пока не появится слово Старт"""
        while True:
            last_message_player = browser.find_element(By.XPATH, self.LAST_MESSAGE_PLAYER_NAME_LOCATOR).text
            first_name, last_name = last_message_player.split()[:2]
            last_message_player_name = first_name + ' ' + last_name

            last_messages = browser.find_elements(By.XPATH, self.LAST_MESSAGE_LOCATOR)
            last_message_element = last_messages[-1].text
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f'Время: {current_time}. Последнее сообщение в чате: {last_message_element} от {last_message_player_name}')
            print('-' * 20)

            if last_message_player_name == 'Рустам Мустафаев' and last_message_element == "Старт":
                print(f"Найдено сообщение 'Старт' от {last_message_player_name}. Начинаем игру")
                self.main_game(browser)
            if last_message_player_name != 'Рустам Мустафаев' and last_message_element == "Старт":
                print(f"Найдено сообщение 'Старт' от {last_message_player_name}. Жду пока меня тегнут")
                self.parser_all_messages(browser)
            if last_message_element == 'Я победил!':
                print('Я победил!')
                return
            if last_message_element == f'Игрок {self.my_player} выбывает.':
                print('Рустам Мустафаев проиграл, вышел из игры')
                return

            time.sleep(2)

    def parser_all_messages(self, browser):
        """Функция парсит чат до тех пор, пока не передадут ход игроку @mustafaev_r"""
        while True:
            last_message = browser.find_elements(By.XPATH, self.LAST_MESSAGE_LOCATOR)
            last_message_element = last_message[-1].text
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f'Время: {current_time}. Последнее сообщение в чате: {last_message_element}')
            print('-' * 20)

            if self.my_player in last_message_element:
                self.main_game(browser)

            # Сохраняем в список города, которые уже использовали
            pattern_city = r'Город\s+([\w\s\-]+)\.'
            match = re.match(pattern_city, last_message_element)
            if match:
                city_name = match.group(1)
                if city_name not in self.used_cities_in_game:
                    self.used_cities_in_game.append(city_name)
                    print(f'Список использованных в игре городов: {self.used_cities_in_game}')

            # Если список игроков пустой, то отправляем сообщение Я победил
            if not self.players:
                send_message(browser, 'Я победил!')
                return

            if f'Игрок {self.my_player} выбывает.' in last_message_element:
                return

            # Если кто-то удалил игрока из игры, то удаляем игрока и из своего списка игроков
            pattern = r"Игрок @(.*?) выбывает\."
            match = re.search(pattern, last_message_element)
            if match:
                username = match.group(1)
                if username in self.players:
                    self.players.remove(username)
                    print(f'Из списка игроков удалили {username}')
                    print(f'Новый список игроков: {self.players}')
            time.sleep(2)

    def main_game(self, browser):
        """Функция отправляет Город игроку и проверяет правильность ответа"""
        print(f'Новый список игроков: {self.players}')

        while True:
            full_cities_list = find_city_json()
            city = random.choice(full_cities_list)
            current_player = choose_opponent(self.players)
            send_turn_message(browser, city, current_player)
            self.used_cities_in_game.append(city)
            print(f'Список использованных в игре городов: {self.used_cities_in_game}')

            while len(self.players) > 0:
                time.sleep(5)
                last_messages = browser.find_elements(By.XPATH, self.LAST_MESSAGE_LOCATOR)
                last_message = last_messages[-1].text

                last_message_player = browser.find_element(By.XPATH, self.LAST_MESSAGE_PLAYER_NAME_LOCATOR)
                last_message_player_name = last_message_player.get_attribute("href")
                last_message_player_name = last_message_player_name[15:]
                print(f'Игрок, который написал последнее сообщение: {last_message_player_name}')
                print(f'Игрок, которому я передал ход: {current_player}')

                # Проверяем, по шаблону сообщение или нет
                try:
                    city_of_last_message = last_message.split()[1][0:-1]
                except IndexError:
                    print(f"Сообщение от игрока {last_message_player_name} не по шаблону")
                    player_out(browser, current_player)
                    self.players.remove(current_player)
                    print(f'Игрок {current_player} ответил неправильно, выбывает из игры, новый список игроков {self.players}')

                    if not self.players:
                        send_message(browser, 'Я победил!')
                        return
                    else:
                        current_player = choose_opponent(self.players) # Если сообщение не по шаблону выбираем нового игрока
                        send_turn_message(browser, city, current_player)
                        continue

                letter_that_compare_1 = city[-1].upper() in 'ЬЪЫ'  # Если последняя буква заканчивается на ьъы
                city_that_compare_1 = city_of_last_message not in self.used_cities_in_game  # Если город не использовался до этого в чате
                player_that_compare_1 = last_message_player_name == current_player  # Если игрок, который ответил и есть тот игрок, которому передавали ход
                player_in_list_1 = last_message_player_name in self.players  # Если игрок, который ответил есть в списке игроков и ранее не выбыл

                letter_that_compare_2 = city[-1].upper() == last_message.split()[1][0].upper()
                city_that_compare_2 = city_of_last_message not in self.used_cities_in_game
                player_that_compare_2 = last_message_player_name == current_player
                player_in_list_2 = last_message_player_name in self.players

                if letter_that_compare_1 and city_that_compare_1 and player_that_compare_1 and player_in_list_1:
                    if city[-2].upper() == last_message.split()[1][0].upper():
                        self.used_cities_in_game.append(city)
                        print(f'Список уже использованных городов: {self.used_cities_in_game}')
                        print('Игрок ответил правильно, возвращаюсь в режим ожидания парсить чат')
                        self.parser_all_messages(browser)
                    else:
                        player_out(browser, current_player)
                        self.players.remove(current_player)
                        print(f'Игрок {current_player} ответил неправильно, выбывает из игры, новый список игроков {self.players}')
                        if not self.players:
                            send_message(browser, 'Я победил!')
                            return
                        else:
                            current_player = choose_opponent(self.players)
                            send_turn_message(browser, city, current_player)
                            continue

                elif letter_that_compare_2 and city_that_compare_2 and player_that_compare_2 and player_in_list_2:
                    self.used_cities_in_game.append(city)
                    print(f'Список уже использованных городов: {self.used_cities_in_game}')
                    print('Игрок ответил правильно, возвращаюсь в режим ожидания парсить чат')
                    self.parser_all_messages(browser)

                else:
                    player_out(browser, current_player)
                    self.players.remove(current_player)
                    print(f'Игрок не ответил, удалили из игры, новый список игроков {self.players}')
                    if not self.players:
                        send_message(browser, 'Я победил!')
                        return
                    else:
                        current_player = choose_opponent(self.players)
                        send_turn_message(browser, city, current_player)
                        continue
            else:
                send_message(browser, 'Я победил!')
                return



































