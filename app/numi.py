import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.config import get_logger, ACC_VENOM_PATH

logger = get_logger(__name__)


CONFIG = {
    "environment": "test",
    "mainnet": {
    },
    "test": {
        "app": {
            "numi": "https://club.numi.net",
        }
    },
}


class Numi(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def buy(self, account: dict = None):
        amount     = self.params.get('amount', "0.01")

        self.driver.get(f"{self.config['app']['numi']}")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        logged_in_twitter = self._check_logged_in_twitter()
        if not logged_in_twitter:
            self.login_twitter(account)
            self.driver.close()

        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(4)
        self.auto.click("//div[contains(text(),'Log In')]", 4)

        # click button Sign up and role tab

        self.auto.click("//button[contains(text(),'Sign up')][@role='tab']", 4)

        # swap
        self.auto.switch_to_window(0)
        inputs = self.auto.try_finds("//input")
        inputs[0].send_keys(amount)
        time.sleep(3)

        self.auto.click("//button[contains(text(),'Swap')]", 4)
        self.auto.click("//button[contains(text(),'Confirm')]", 4)
        self.auto.confirm(account['password'])
        logger.info(f"Incentive success")


if __name__ == '__main__':
    # list_account = AccountLoader().parser_file()
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[1],
    }
    params = {
        "list_add": list_account,
        "amount": "1",
        "from_token": "VENOM",
        "to_token": "USDT",
    }
    try:
        vn = Web3World(
            use_uc=True,
            params=params
        )
        vn.process_all(method="swap")
        # vn.swap(**swap_params)
    except Exception as e:
        logger.error(e)
