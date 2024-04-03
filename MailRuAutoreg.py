from random import randint, choices
from requests import post, get
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent
from loguru import logger
from multiprocessing import Process
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

# Загрузка ключа из секции [token]
token = config['token']['key']

# Загрузка других настроек
session_count = int(config['settings']['session_count'])
headless = config.getboolean('settings', 'headless')

chars_name = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
chars_password = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()-_@$!&?'
url = "https://account.mail.ru/signup?back=https%3A%2F%2Faccount.mail.ru%2Fregister%3Fauthid%3Dlc7psg5f.6h7%26dwhsplit%3Ds10273.b1ss12743s%26from%3Dlogin&dwhsplit=s10273.b1ss12743s&from=login"

ua = UserAgent()


def generate_random_string(ln, chars):
    password = ''.join(choices(chars, k=ln))
    return password


def convert_account_data_to_string(account_data):
    email = account_data['email']
    fname = account_data['fname']
    lname = account_data['lname']
    password = account_data['password']
    reserve_mail = account_data['reserve_mail']

    result = f'{email}\t{fname}\t{lname}\t{password}\t{reserve_mail}'

    return result


@logger.catch()
def check_captcha(img, session_id):
    try:
        r = post('http://rucaptcha.com/in.php',
                 data={'key': token, 'method': 'base64', 'body': img, 'phrase': 0, 'regsense': 0,
                       'lang': 'en'}).text

        logger.debug(f'{session_id}: request - {r}')
        capcha_id = ''

        if r[:2] == 'OK':
            capcha_id = r[3:]
        else:
            return False

        for i in range(10):
            sleep(2)
            result = get(f'http://rucaptcha.com/res.php?key={token}&action=get&id={capcha_id}').text
            if result[:2] == 'OK' and len(result[3:]) == 6:
                logger.debug(f'{session_id}: {result}')
                return result[3:]
            elif result == 'CAPCHA_NOT_READY':
                continue
            else:
                logger.error(f'{session_id}: Вернул неверную капчу')
                return False
        return False
    except Exception as ex:
        logger.error(f'{session_id}: Oшибка при запросе капчи: {ex}')


@logger.catch()
def initialize_driver(session_id):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={ua.random}')
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('disable-notifications')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        if headless:
            options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)

        return driver
    except Exception as ex:
        logger.error(f'{session_id}: Error during driver initialization: {ex}')


@logger.catch()
def register_email(session_id):
    driver = initialize_driver(session_id)
    if driver is None:
        return False
    logger.info(f'{session_id}: start registration...')
    try:
        driver.get(url)
    except Exception as ex:
        driver.quit()
        sleep(10)
        logger.error(f'{session_id}: Oшибка при открытии страницы: {ex}')
        return False

    logger.info(f'{session_id}: window was opened...')

    if len(driver.find_elements(By.ID, 'preloader')) != 0:
        while len(driver.find_elements(By.ID, 'preloader')) != 0:
            sleep(1)
            driver.refresh()

    try:
        sleep(2)

        fname = generate_random_string(6, chars_name)
        lname = generate_random_string(6, chars_name)
        username = generate_random_string(10, chars_name)
        reserve_mail = f'{generate_random_string(10, chars_name)}@rambler.ru'

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.NAME, 'fname'))
        ).send_keys(fname)

        driver.find_element(by=By.NAME, value='lname').send_keys(lname)
        driver.find_element(by=By.NAME, value='partial_login').send_keys(username)

        element_to_remove = driver.find_element(by=By.CSS_SELECTOR, value='div.border-0-2-155')
        driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element_to_remove)
        element_to_remove = driver.find_element(by=By.CSS_SELECTOR, value='div.background-0-2-154')
        driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element_to_remove)

        driver.find_element(by=By.XPATH, value='//input[@value="male"]').click()
        driver.find_element(by=By.LINK_TEXT, value='Указать резервную почту').click()
        driver.find_element(by=By.LINK_TEXT, value='Сгенерировать надёжный пароль').click()

        password = driver.find_element(by=By.NAME, value='password').get_attribute("value")

        driver.find_elements(by=By.CLASS_NAME, value='Select__value-container')[0].click()
        driver.find_elements(by=By.CLASS_NAME, value='Select__option')[7].click()
        driver.find_elements(by=By.CLASS_NAME, value='Select__value-container')[1].click()
        driver.find_elements(by=By.CLASS_NAME, value='Select__option')[2].click()
        driver.find_elements(by=By.CLASS_NAME, value='Select__value-container')[2].click()
        driver.find_elements(by=By.CLASS_NAME, value='Select__option')[30].click()
        driver.find_element(by=By.NAME, value='email').send_keys(reserve_mail)
        driver.find_elements(by=By.XPATH, value="//button[@type='submit']")[1].click()

        account_data = {
            'email': f'{username}@mail.ru',
            'fname': fname,
            'lname': lname,
            'password': password,
            'reserve_mail': reserve_mail,
        }

        logger.debug(f'{session_id}: {username}@mail.ru\t{password}\t{reserve_mail}\t')
    except Exception as ex:
        logger.error(f'{session_id}: Oшибка при взаимодействии с объектами на странице ввода данных: {ex}')
        driver.quit()
        return False

    try:
        sleep(1)
        if len(driver.find_elements(by=By.ID,
                                    value='phone-number__phone-input')) != 0:
            logger.info(f'{session_id}: Требует телефон')
            driver.quit()
            return False

        for i in range(5):
            try:
                sleep(2)
                img = driver.find_elements(by=By.TAG_NAME, value="img")[1].screenshot_as_base64
                if len(img) < 12000:
                    continue
                else:
                    if len(img) == 7860:
                        driver.quit()
                        return False
                    else:
                        break
            except Exception as ex:
                driver.quit()
                logger.error(ex)
                return False

        img = driver.find_elements(by=By.TAG_NAME, value="img")[1].screenshot_as_base64
        logger.info(f'{session_id}: {len(img)}')
        if len(img) > 12000:
            img = driver.find_elements(by=By.TAG_NAME, value="img")[1].screenshot_as_base64
            result = check_captcha(img, session_id)
            if not result:
                driver.quit()
                return False
        else:
            driver.quit()
            return False

        driver.find_element(by=By.CLASS_NAME, value='input-0-2-119').send_keys(result)
        driver.find_elements(by=By.XPATH, value="//button[@type='submit']")[0].click()
        sleep(1)
        if driver.find_elements(by=By.LINK_TEXT,
                                value='Регистрация без номера телефона невозможна. Вернитесь к предыдущему шагу и укажите номер телефона'):
            driver.quit()
            return False

        if driver.find_elements(by=By.LINK_TEXT, value='Вы указали неправильный код с картинки'):
            driver.quit()
            return False
        sleep(5)
        driver.quit()
        return account_data
    except Exception as ex:
        driver.quit()
        logger.error(f'{session_id}: Oшибка при работе c капчей: {ex}')


@logger.catch()
def check_registration(email, session_id):
    try:
        logger.info(f'{session_id}: Проверка регистрации {email}')

        driver_check = initialize_driver(session_id)
        check_url = 'https://account.mail.ru/login?page=https%3A%2F%2Faccount.mail.ru%2F%3F&'

        driver_check.get(check_url)

        sleep(10)

        username = WebDriverWait(driver_check, 60).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )

        username.send_keys(email)
        driver_check.find_elements(by=By.XPATH, value="//button[@type='submit']")[0].click()
        sleep(2)
        if len(driver_check.find_elements(by=By.CLASS_NAME, value="login-header")) != 0:
            driver_check.quit()
            return True
        else:
            driver_check.quit()
            return False
    except Exception as ex:
        logger.error(f'{session_id}: ошибка при проверке регистрации: {ex}')


@logger.catch()
def run_registration_process(session_id):
    logger.info(f'{session_id}:  Start program...')
    while True:
        sleep(3)
        driver = initialize_driver(session_id)
        if driver is None:
            while True:
                driver = initialize_driver(session_id)
                sleep(5)
                if driver is not None:
                    break
        while True:
            sleep(randint(1, 3))
            try:
                account_data = register_email(session_id)
                if account_data:
                    email = account_data['email']
                    if check_registration(email, session_id):
                        with open(f"../MailRu-autoreg/src/Autoreg_MailRU.txt", "a") as file:
                            email = account_data['email']
                            account_data_str = convert_account_data_to_string(account_data=account_data)
                            file.write(account_data_str + '\n')  # Дописываем новую запись в файл
                            logger.info(f'{session_id}: {email} Успешно зарегистрирован')
                            file.close()
                    else:
                        logger.info(f'{session_id}: {email} Не зарегистрирован')
                        break
                else:
                    driver.quit()
                    break
            except Exception as ex:
                logger.error(f'{session_id}: {ex}')
                break
            finally:
                driver.quit()


@logger.catch()
def main():
    processes = []
    for session_id in range(session_count):
        sleep(0.1)
        process = Process(target=run_registration_process, args=(session_id,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
