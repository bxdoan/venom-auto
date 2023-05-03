import time
import pandas as pd
from app.enums import GasPrice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

from app import utils
from app.config import get_logger, PASSWORD, CODE_HOME, WIDTH, HEADLESS, EXTENSION_ID, \
    EXTENSION_DIR, DRIVER_PATH, HEIGHT, EXTENSION_CRX

logger = get_logger(__name__)

# download the newest version of keplr extension from:
# ref. https://chrome.google.com/webstore/detail/keplr/dmkamcknogkgcdfhhbddcghachkejeap
# or from  https://github.com/chainapsis/keplr-wallet
# EXT_URL = f"chrome-extension://ojggmchlghnjlapmfbnjholfjkiidbch/popup.html"
EXT_URL = f"chrome-extension://{EXTENSION_ID}/home.html"
POPUP_URL = f"chrome-extension://{EXTENSION_ID}/popup.html"
FILE_NAME = f"{CODE_HOME}/account.venom1.csv"


def launchSeleniumWebdriver(use_uc=True) -> webdriver:
    if use_uc:
        options = uc.ChromeOptions()
        options.add_argument(f"--load-extension={EXTENSION_DIR}")
    else:
        options = webdriver.ChromeOptions()
        options.add_extension(EXTENSION_CRX)

    prefs = {
        "extensions.ui.developer_mode": True,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)

    # add headless option
    if utils.force2bool(HEADLESS):
        logger.info('headless mode')
        options.add_argument('--headless')

    global driver
    if use_uc:
        driver = uc.Chrome(options=options, executable_path=DRIVER_PATH)
    else:
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    driver.set_window_size(WIDTH, HEIGHT)
    logger.info(f"Extension has been loaded successfully ")
    time.sleep(5)
    driver.refresh()
    return driver


def try_find(xpath="", by=By.XPATH):
    try:
        return driver.find_element(by, xpath)
    except Exception as _e:
        return None


def try_finds(xpath="", by=By.XPATH):
    try:
        return driver.find_elements(by, xpath)
    except Exception as _e:
        return []


def walletSetup(recoveryPhrase: 'str', password: str) -> None:
    driver.execute_script("window.open('');")
    time.sleep(3)  # wait for the new window to open
    switch_to_window(0)
    driver.refresh()
    switch_to_window(2)
    driver.get(f"chrome://extensions/?id={EXTENSION_ID}")
    time.sleep(2)

    ext_ma = driver.find_element(By.CSS_SELECTOR, "extensions-manager")
    sr1 = ext_ma.shadow_root
    cr_view_manager = sr1.find_element(By.CSS_SELECTOR, "cr-view-manager")
    ext_detail_view = cr_view_manager.find_element(By.CSS_SELECTOR, "extensions-detail-view")
    sr3 = ext_detail_view.shadow_root
    buttons = sr3.find_elements(By.CLASS_NAME, "inspectable-view")
    buttons[1].click()
    time.sleep(5)
    switch_to_window(2)
    driver.close()
    switch_to_window(0)
    try_click("//div[contains(text(),'Sign in with seed phrase')]", 2)

    # fill in recovery seed phrase
    inputs = try_finds('//input')
    list_of_recovery_phrase = recoveryPhrase.split(" ")
    for i, x in enumerate(list_of_recovery_phrase):
        phrase = list_of_recovery_phrase[i]
        inputs[i].send_keys(phrase)

    try_click("//div[contains(text(),'Confirm')]", 2)

    # fill in password
    inputs = try_finds('//input')
    inputs[0].send_keys(password)
    inputs[1].send_keys(password)
    time.sleep(1)
    try_click("//div[contains(text(),'Sign in the')]", 10)
    switch_to_window(0)
    time.sleep(2)


def try_click(xpath, time_to_sleep=None, by=By.XPATH, wd=None) -> None:
    try:
        click(xpath, time_to_sleep, by, wd)
    except:
        pass


def try_get_text(xpath, by=By.XPATH) -> str:
    try:
        return try_find(xpath, by).text
    except:
        return ''


def click(xpath, time_to_sleep=None, by=By.XPATH, wd=None) -> None:
    if time_to_sleep is None:
        time_to_sleep = 1
    if wd is None:
        wd = driver
    # Click once.
    # If click more times, try another method.
    button = wd.find_element(by, xpath)
    try:
        logger.info(f'click on "{button.text}"')
    except:
        pass
    clicking = ActionChains(wd).click(button)
    clicking.perform()
    time.sleep(time_to_sleep)


def insert_text(xpath, text) -> None:
    input_text = driver.find_element(By.XPATH, xpath)
    input_text.send_keys(text)
    time.sleep(0.5)


def sign():
    switch_to_window(-1)
    inputs = try_finds("//input")
    inputs[0].send_keys(PASSWORD)
    driver.try_click("//div[contains(text(),'Sign')]", 10)


def send(receiver : str, amount : str) -> None:
    driver.execute_script("window.open('');")
    switch_to_window(-1)
    driver.get(POPUP_URL)
    time.sleep(4)
    driver.try_click("//div[contains(text(),'Send')]", 4)
    switch_to_window(-1)
    inputs = try_finds("//input")
    inputs[0].send_keys(receiver)
    inputs[1].send_keys(amount)
    inputs[2].send_keys(PASSWORD)
    driver.try_click("//div[contains(text(),'Confirm transaction')]", 4)
    switch_to_window(-1)
    driver.close()


def confirm():
    switch_to_window(-1)
    inputs = try_finds("//input")
    inputs[0].send_keys(PASSWORD)
    driver.try_click("//div[contains(text(),'Confirm tran')]", 10)


def process_acc(idx):
    seed_phrase = addr = ''
    try:
        try_click("//div[contains(text(),'Create a')]", 2)
        try_click("//input[@type='checkbox']")
        try_click("//div[contains(text(),'Submit')]", 2)

        list_li = try_finds("//li")
        mnemonic = [li.text for li in list_li if li.text != '']
        seed_phrase = ' '.join(mnemonic)
        logger.info(f"seed phrase: {seed_phrase}")
        try_click("//div[contains(text(),'I wrote it')]", 2)

        locate_m = try_finds("//span")
        list_locate = [int(li.text.split('.')[0]) for li in locate_m if li.text != '']

        inputs = try_finds("//input")
        for i, x in enumerate(list_locate):
            inputs[i].send_keys(mnemonic[int(x)-1])

        time.sleep(2)
        try_click("//div[contains(text(),'Confirm')]", 2)

        passes = try_finds("//input")
        passes[0].send_keys(PASSWORD)
        passes[1].send_keys(PASSWORD)
        try_click("//div[contains(text(),'Create the wallet')]", 2)

        switch_to_window(0)
        driver.get(f"{POPUP_URL}")
        time.sleep(3)
        try_click("//span[contains(text(),'VENOM')]", 2)
        try_click("//div[contains(text(),'Receive')]", 4)

        addr = try_get_text("//*[@id='root']/div[2]/div[2]/div[2]/div/div[3]/div[2]/div[2]/div/div[3]/div/div[1]/div[2]/div/span")

    except Exception as _e:
        logger.error(_e)
    return seed_phrase, addr


def get_address():
    addr = ''
    try:
        # get address
        driver.execute_script("window.open('');")
        time.sleep(2)
        switch_to_window(1)
        driver.get(f"{EXT_URL}")
        time.sleep(2)
        click(f'//*[@id="app"]/div/div[1]/div[2]/div/div[2]/div/div[1]', 2)

        addr = driver.find_element(By.CLASS_NAME, 'address-tooltip').text
        driver.close()
        switch_to_window(0)
        time.sleep(5)
    except:
        pass
    return addr


def open_window():
    driver.execute_script("window.open('');")
    time.sleep(3)


def switch_to_window(window_number):
    # Switch to another window, start from 0.
    try:
        wh = driver.window_handles
        logger.info(f'window handles: {len(wh)}')
        driver.switch_to.window(wh[window_number])
    except:
        pass
    logger.info(f'switched to window numer: {str(window_number)}')


def approve(gas=GasPrice.Average):
    time.sleep(3)
    switch_to_window(-1)
    if gas in GasPrice.all():
        try:
            click(f"//div[text()='{gas}']")
        except Exception as _e:
            pass

    try:
        click("//button[text()='Approve']", 5)
    except Exception as _e:
        pass


def reject():
    try:
        time.sleep(4)
        switch_to_window(-1)
        click("//button[text()='Reject']", 5)
    except:
        pass


def create_account(index):
    mns = pd.DataFrame(columns=["Name", "Address", "Private Key", "Seed Phrase",
                                "Password", "Status"])
    switch_to_window(0)
    seed_phrase, addr = process_acc(index)

    if seed_phrase:
        row = [f"", addr, "", seed_phrase, PASSWORD, '']
        mns.loc[len(mns)] = row
        utils.add_to_csv(FILE_NAME, mns.loc[0])
        logger.info(f"Create account success with address: {addr} and seed phrase: {seed_phrase}")
    else:
        logger.info(f"Create account fail")


if __name__ == '__main__':
    for i in range(0, 300):
        driver = launchSeleniumWebdriver(False)
        try:
            create_account(index=i)
        except Exception as e:
            logger.info(e)

        driver.quit()
