import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.config import get_logger, ACC_VENOM_PATH, DAILY_ANSWER

logger = get_logger(__name__)


CONFIG = {
    "environment": "test",
    "mainnet": {
    },
    "test": {
        "app": {
            "snipa": "https://venom.snipa.finance",
        }
    },
}


class Snipa(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def incentive(self, account: dict = None):
        if not self.driver:
            self._try_start_driver(account)

        self.driver.get(f"{self.config['app']['snipa']}")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        logged_in_wallet = self._check_logged_in_wallet()
        if not logged_in_wallet:
            self.auto.walletSetup(account['seed_phrase'], account['password'])

        self.auto.switch_to_window(0)
        # logged_in_twitter = self._check_logged_in_twitter()
        # if not logged_in_twitter:
        #     self.login_twitter(account)
        #     self.driver.close()
        # self._tweet()
        # self._follow(account)

        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(8)

        # connect venom wallet
        self.auto.click("//span[contains(text(),'ogin via Walle')]", 2)
        self.auto.click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.click("//div[contains(text(),'Connect')]", 3)

        self.auto.switch_to_window(-1)
        self.auto.click("//div[contains(text(),'Join Venom Testnet')]", 3)
        self.auto.confirm(password=account['password'])

        self.auto.switch_to_window(-1)
        url = f"https://venom.network/tasks"
        self.driver.get(url)
        time.sleep(2)
        self._connect_wallet()
        self.auto.switch_to_window(0)
        self._daily_faucet(account)

        logger.info(f"Incentive success")


if __name__ == '__main__':
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[4],
    }
    params = {
        "list_add": list_account,
        "answer": DAILY_ANSWER,
    }
    try:
        vn = Snipa(
            use_uc=True,
            params=params

        )
        vn.process_all(method="incentive")
        # vn.incentive(**swap_params)
    except Exception as e:
        logger.error(e)
