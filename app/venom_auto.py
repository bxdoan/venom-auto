import time
from selenium.webdriver.common.by import By

from wallet import venom
from app.account import AccountLoader
from app.base import VenomAuto
from app.config import get_logger, ACC_VENOM_PATH

logger = get_logger(__name__)


CONFIG = {
    "environment": "test",
    "mainnet": {
    },
    "test": {
        "twitter": {
            "venom_network": "https://twitter.com/Venom_network_",
            "venom_foundation": "https://twitter.com/VenomFoundation",
            "create_post": "https://twitter.com/intent/tweet?text=Just%20claimed%20my%20first%20faucet%20tokens%20and%20am%20ready%20to%20use%20them%20on%20the%20%23VenomTestnet!%20Get%20them%20yourself%20on%20https%3A%2F%2Fvenom.network",
        },
        "task": {
            "venom_foundation": "https://venom.network/tasks/venom-foundation",
        }
    },
}


class Venom(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def incentive(self, account: dict = None):

        url = f"https://venom.network/tasks"
        self.driver.get(url)
        time.sleep(2)

        # close wellcome popup
        self.auto.switch_to_window(0)
        # self.login_twitter(account)

        # setup metamask with seed phrase and password
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        # click on the Connect Wallet button
        self.auto.switch_to_window(1)
        self.auto.try_click("//span[contains(text(),'Connect Wallet')]", 2)
        self.auto.try_click("//span[contains(text(),'Venom Chrome')]", 3)
        self.auto.try_click("//span[contains(text(),'Connect')]", 3)

        self._foundation(account)

        logger.info(f"Incentive success")

    def _following(self, url: str):
        self.driver.execute_script("window.open('');")
        self.auto.switch_to_window(-1)
        self.driver.get(url)
        time.sleep(2)
        self.auto.try_click("//span[contains(text(),'Follow')]", 4)
        self.driver.close()

    def _foundation(self, acc: dict = None):
        self.driver.execute_script("window.open('');")
        self.auto.switch_to_window(-1)
        self.driver.get(self.config['twitter']['create_post'])
        time.sleep(2)
        self.auto.try_click("//span[contains(text(),'Tweet')]", 2)
        self.driver.close()

        self._following(self.config['twitter']['venom_network'])

        self.auto.switch_to_window(0)
        self.driver.execute_script("window.open('');")
        self.auto.switch_to_window(-1)
        self.driver.get(self.config['twitter']['venom_foundation'])

        checks = self.auto.try_finds("//span[contains(text(),'Check')]")
        for check in checks:
            check.click()
            time.sleep(2)

        self.auto.try_click("//span[contains(text(),'Claim')]", 2)


if __name__ == '__main__':
    # list_account = AccountLoader().parser_file()
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[0],
    }
    params = {
        "list_add": list_account,
    }
    try:
        Venom(
            use_uc=True,
            params=params
        ).incentive(**swap_params)
    except Exception as e:
        logger.error(e)
