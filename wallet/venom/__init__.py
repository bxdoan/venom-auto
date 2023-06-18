import time
import pandas as pd
from app.enums import GasPrice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

from app import utils
from app.config import get_logger, PASSWORD, CODE_HOME, WIDTH, HEADLESS, EXTENSION_ID, \
    HEIGHT, EXTENSION_META_DIR, DEFAULT_EXTENSION, DEFAULT_WAIT_CONFIRM

logger = get_logger(__name__)

# download the newest version of keplr extension from:
# ref. https://chrome.google.com/webstore/detail/keplr/dmkamcknogkgcdfhhbddcghachkejeap
# or from  https://github.com/chainapsis/keplr-wallet
# EXT_URL = f"chrome-extension://ojggmchlghnjlapmfbnjholfjkiidbch/popup.html"
EXT_URL = f"chrome-extension://{EXTENSION_ID}/home.html"
POPUP_URL = f"chrome-extension://{EXTENSION_ID}/popup.html"
FILE_NAME = f"{CODE_HOME}/account.venom2.csv"


def launchSeleniumWebdriver(with_meta=False, address : str = None) -> webdriver:
    options = uc.ChromeOptions()

    if with_meta:
        options.add_argument(f"--load-extension={DEFAULT_EXTENSION},{EXTENSION_META_DIR}")
    else:
        options.add_argument(f"--load-extension={DEFAULT_EXTENSION}")

    user_data_dir = utils.user_data_dir(address=address)
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")

    options.add_argument("--disable-popup-blocking")

    prefs = {
        "extensions.ui.developer_mode"    : True,
        "credentials_enable_service"      : False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)

    # add headless option
    if utils.force2bool(HEADLESS):
        logger.info('headless mode')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')

    global driver
    driver = uc.Chrome(options=options)

    driver.set_window_size(WIDTH, HEIGHT)
    logger.info(f"Extension has been loaded successfully ")
    time.sleep(5)
    driver.refresh()
    utils.get_ip()
    return driver


def walletSetup(recoveryPhrase: 'str', password: str) -> None:
    logger.info(f"walletSetup with recoveryPhrase: {recoveryPhrase}")
    # switch_to_window(0)
    # time.sleep(8)
    driver.execute_script("window.open('');")
    time.sleep(5)  # wait for the new window to open
    switch_to_window(0)
    time.sleep(3)
    if len(driver.window_handles) > 1:
        switch_to_window(-1)
    driver.get(f"chrome://extensions/?id={EXTENSION_ID}")
    time.sleep(5)
    ext_ma = driver.find_element(By.CSS_SELECTOR, "extensions-manager")
    toolbar = ext_ma.shadow_root.find_element(By.CSS_SELECTOR, "extensions-toolbar")
    update_button = toolbar.shadow_root.find_element(By.ID, "updateNow")
    update_button.click()
    time.sleep(8)

    if len(driver.window_handles) == 3:
        switch_to_window(0)
        time.sleep(2)
        driver.close()
        time.sleep(2)
    elif len(driver.window_handles) == 1:
        driver.execute_script("window.open('');")
        time.sleep(3)
        switch_to_window(-1)

    driver.get(EXT_URL)
    time.sleep(5)

    if len(driver.window_handles) == 1:
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
    time.sleep(7)


def try_find(xpath="", by=By.XPATH):
    try:
        return driver.find_element(by, xpath)
    except Exception as e:
        logger.error(f"Find {xpath} {by} error: {str(e)}")
        return None


def try_finds(xpath="", by=By.XPATH):
    try:
        return driver.find_elements(by, xpath)
    except Exception as _e:
        logger.error(f"Finds {xpath} {by} error: {str(e)}")
        return []


def try_send_keys(xpath="", msg="", time_to_wait=5, by=By.XPATH) -> None:
    try:
        driver.find_element(by, xpath).send_keys(msg)
        time.sleep(time_to_wait)
    except Exception as _e:
        logger.error(f"Send key {xpath} {msg} {by} error: {str(_e)}")


def open_new_tab(url, time_to_wait=5):
    driver.execute_script("window.open('');")
    switch_to_window(-1)
    driver.get(url)
    time.sleep(time_to_wait)


def metamaskSetup(recoveryPhrase : 'str', password : str) -> None:
    driver.open_new_tab(f"{EXT_URL}#onboarding/welcome")
    time.sleep(4)
    window_before = driver.window_handles
    driver.switch_to.window(window_before[-1])
    click('//button[text()="Import an existing wallet"]')

    click('//button[text()="No thanks"]')

    # fill in recovery seed phrase
    inputs = driver.find_elements(By.XPATH, '//input')
    list_of_recovery_phrase = recoveryPhrase.split(" ")
    for i, x in enumerate(list_of_recovery_phrase):
        if i == 0:
            locate_input = i
        else:
            locate_input = i * 2
        phrase = list_of_recovery_phrase[i]
        inputs[locate_input].send_keys(phrase)

    click('//button[text()="Confirm Secret Recovery Phrase"]')

    # fill in password
    inputs = driver.find_elements(By.XPATH, '//input')
    inputs[0].send_keys(password)
    inputs[1].send_keys(password)

    click('.create-password__form__terms-label', 1, By.CSS_SELECTOR)

    click('//button[text()="Import my wallet"]')

    click('//button[text()="Got it!"]')

    click('//button[text()="Next"]')

    click('//button[text()="Done"]')

    logger.info("Wallet has been imported successfully")

    # Close the popup
    click('//*[@id="popover-content"]/div/div/section/div[2]/div/button')
    driver.switch_to.window(driver.window_handles[0])


def try_click(xpath, time_to_sleep=None, by=By.XPATH, wd=None) -> None:
    try:
        click(xpath, time_to_sleep, by, wd)
    except Exception as e:
        logger.error(f"Click {xpath} {by} error: {str(e)}")


def try_get_text(xpath, by=By.XPATH) -> str:
    try:
        return try_find(xpath, by).text
    except Exception as e:
        logger.error(f"Get text {xpath} {by} error: {str(e)}")
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


def send(receiver : str, amount : str) -> None:
    open_new_tab(POPUP_URL)

    click("//div[contains(text(),'Send')]", 4)
    switch_to_window(-1)
    inputs = try_finds("//input")
    inputs[1].send_keys(receiver)
    inputs[2].send_keys(amount)
    if len(inputs) == 4:
        # if have password field
        inputs[3].send_keys(PASSWORD)
    time.sleep(5)
    click("//div[contains(text(),'Confirm transaction')]", 4)
    switch_to_window(-1)
    try_click("//div[contains(text(),'Ok')]", 4)


def confirm(password : str = PASSWORD, time_to_sleep : int = DEFAULT_WAIT_CONFIRM) -> bool:
    switch_to_window(-1)
    inputs = try_finds("//input")
    if inputs:
        inputs[0].send_keys(password)
        click("//span[contains(text(),'Remember')]", 2)
    click("//div[contains(text(),'Confirm tran')]", time_to_sleep)
    return True


def sign(tts : int = DEFAULT_WAIT_CONFIRM) -> bool:
    switch_to_window(-1)
    inputs = try_finds("//input")
    if len(inputs) > 0:
        inputs[0].send_keys(PASSWORD)
    switch_to_window(-1)
    click("//button[@type='submit']", tts)
    return True


def process_acc(idx):
    seed_phrase = addr = ''
    try:
        # driver.get(f"chrome://extensions/?id={EXTENSION_ID}")
        # time.sleep(5)
        #
        # ext_ma = driver.find_element(By.CSS_SELECTOR, "extensions-manager")
        # toolbar = ext_ma.shadow_root.find_element(By.CSS_SELECTOR, "extensions-toolbar")
        # update_button = toolbar.shadow_root.find_element(By.ID, "updateNow")
        # update_button.click()
        # time.sleep(5)
        # driver.get(EXT_URL)
        # time.sleep(8)

        try_click("//div[contains(text(),'Create a')]", 2)
        try_click('/html/body/div/div[1]/div/div[2]/div/div/div[2]/label/span', 2)
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
        driver.open_new_tab(f"{EXT_URL}")
        time.sleep(4)
        switch_to_window(1)
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


def switch_to_window(window_number : int = 0) -> None:
    # Switch to another window, start from 0.
    wh = driver.window_handles
    try:
        driver.switch_to.window(wh[window_number])
    except:
        pass
    logger.info(f'window handles: {len(wh)} and switch {str(window_number)}')


def approve(gas : str = GasPrice.Average) -> None:
    time.sleep(3)
    switch_to_window(-1)

    if gas in GasPrice.all():
        try_click(f"//div[text()='{gas}']")

    try_click("//button[contains(text(),'Approve')]", 5)


def reject():
    time.sleep(4)
    try:
        switch_to_window(-1)
        click("//button[contains(text(),'Reject')]", 5)
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
    for i in range(0, 150):
        driver = launchSeleniumWebdriver()
        try:
            create_account(index=i)
        except Exception as e:
            logger.info(e)

        driver.quit()
