import time
import pandas as pd
from app.enums import GasPrice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

from app import utils
from app.config import get_logger, PASSWORD, CODE_HOME, WIDTH, HEADLESS, EXTENSION_ID_KEPLR, \
    EXTENSION_DIR, EXTENSION_DIR_LEAP, DRIVER_PATH, HEIGHT

logger = get_logger(__name__)

# download the newest version of keplr extension from:
# ref. https://chrome.google.com/webstore/detail/keplr/dmkamcknogkgcdfhhbddcghachkejeap
# or from  https://github.com/chainapsis/keplr-wallet
EXTENSION_ID = EXTENSION_ID_KEPLR or 'npdbcbhdknmoephofajnekpbocjpphdd'
EXT_URL = f"chrome-extension://{EXTENSION_ID}/popup.html"
CHAIN_ID = 'atlantic-2'
CHAIN_NAME = f'Sei {CHAIN_ID}'
FILE_NAME = f"{CODE_HOME}/account.sei.csv"


def launchSeleniumWebdriver() -> webdriver:
    options = uc.ChromeOptions()
    options.add_argument(f"--load-extension={EXTENSION_DIR},{EXTENSION_DIR_LEAP}")
    prefs = {
        "extensions.ui.developer_mode": True,
    }
    options.add_experimental_option("prefs", prefs)

    # add headless option
    if utils.force2bool(HEADLESS):
        logger.info('headless mode')
        options.add_argument('--headless')

    global driver
    driver = uc.Chrome(options=options, executable_path=DRIVER_PATH)
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


def walletSetup(recoveryPhrase : 'str', password : str) -> None:
    driver.execute_script("window.open('');")
    time.sleep(5)  # wait for the new window to open
    switch_to_window(-1)
    driver.get(f"{EXT_URL}")
    time.sleep(2)
    switch_to_window(-1)
    time.sleep(2)
    click('//*[@id="app"]/div/div[3]/button[3]', 2)
    switch_to_window(-1)

    # fill in recovery seed phrase
    inputs = try_finds('//input')
    list_of_recovery_phrase = recoveryPhrase.split(" ")
    for i, x in enumerate(list_of_recovery_phrase):
        phrase = list_of_recovery_phrase[i]
        inputs[i].send_keys(phrase)

    # fill in password
    inputs[12].send_keys("Don")
    inputs[13].send_keys(password)
    inputs[14].send_keys(password)
    time.sleep(2)
    click('//button[text()="Next"]', 2)

    click('//button[text()="Done"]', 5)

    switch_to_window(0)
    time.sleep(2)


def try_click(xpath, time_to_sleep = None, by=By.XPATH) -> None:
    try:
        click(xpath, time_to_sleep, by)
    except:
        pass


def click(xpath, time_to_sleep = None, by=By.XPATH) -> None:
    if time_to_sleep is None:
        time_to_sleep = 1
    # Click once.
    # If click more times, try another method.
    button = driver.find_element(by, xpath)
    try:
        logger.info(f'click on "{button.text}"')
    except:
        pass
    clicking = ActionChains(driver).click(button)
    clicking.perform()
    time.sleep(time_to_sleep)


def insert_text(xpath, text) -> None:
    input_text = driver.find_element(By.XPATH, xpath)
    input_text.send_keys(text)
    time.sleep(0.5)


def process_acc(idx):
    mnemonic = ''
    try:
        click("//button[text()='Create new account']")

        mnemonic = driver.find_element(By.XPATH, "//*[@id='app']/div/div[3]/div/form/div[1]").text

        insert_text("//input[@name='name']", f"don{idx}")

        insert_text("//input[@name='password']", PASSWORD)
        insert_text("//input[@name='confirmPassword']", PASSWORD)

        click("//button[text()='Next']")

        # create mnemonic
        list_mnemonic = mnemonic.split(' ')
        for btn_test in list_mnemonic:
            click(f"//button[text()='{btn_test}']", 0.1)

        click("//button[text()='Register']")
        click("//button[text()='Done']")
    except:
        pass
    return mnemonic


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

        click(f"//div[text()='{CHAIN_NAME}']", 2)

        addr = driver.find_element(By.CLASS_NAME, 'address-tooltip').text
        driver.close()
        switch_to_window(0)
        time.sleep(5)
    except:
        pass
    return addr


def switch_to_window(window_number):
    # Switch to another window, start from 0.
    try:
        wh = driver.window_handles
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
    driver.get("https://app.seinetwork.io/faucet")
    driver.execute_script("window.open('');")
    time.sleep(5)
    switch_to_window(1)
    driver.get(f"{EXT_URL}#/register")
    mn = process_acc(index)
    switch_to_window(0)
    time.sleep(5)

    click("//button[text()='connect wallet']", 3)

    click("//p[text()='keplr']", 3)

    switch_to_window(-1)

    approve()
    switch_to_window(0)

    addr = get_address()

    row = [f"", addr, "", mn, PASSWORD, '']
    mns.loc[len(mns)] = row
    utils.add_to_csv(FILE_NAME, mns.loc[i])

    driver.quit()

    logger.info(f"Create account success")


if __name__ == '__main__':
    for i in range(0, 1):
        driver = launchSeleniumWebdriver()
        try:
            create_account(index=i)
        except Exception as e:
            logger.info(e)
            driver.quit()
