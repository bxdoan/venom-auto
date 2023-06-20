import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.config import get_logger, ACC_VENOM_PATH, CODE_HOME

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
        self.list_tw_follow = kwargs.get('list_tw_follow') or []

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def buy(self, account: dict = None):
        if not self.driver:
            self._try_start_driver(account)

        self.driver.get(f"{self.config['app']['numi']}")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        logged_in_twitter = self._check_logged_in_twitter()
        if not logged_in_twitter:
            self.login_twitter(account)
            self.driver.close()

        self._tweet()
        self._follow_list(account=account, list_acc=self.list_tw_follow)

        self.auto.switch_to_window(0)
        self.auto.click("//div[contains(text(),'Log In')]", 3)

        # click button Sign up and role tab
        self.auto.click("//button[contains(text(),'Sign up')][@role='tab']", 3)

        # sign up
        self.auto.switch_to_window(0)
        inputs = self.auto.try_finds("//input")
        inputs[0].send_keys(account['tw_acc'])
        time.sleep(0.3)
        inputs[1].send_keys(account['tw_email'])
        time.sleep(0.3)
        inputs[2].send_keys(account['password'])
        time.sleep(0.3)
        inputs[3].send_keys(account['password'])
        time.sleep(0.3)
        inputs[4].click()
        time.sleep(0.3)
        inputs[5].click()
        time.sleep(0.3)
        self.auto.click("//div[contains(text(),'Sign up')]", 3)

        self.auto.switch_to_window(0)
        self.auto.click("//div[contains(text(),'Connect wallet')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.click("//div[contains(text(),'Connect')]", 3)
        self.auto.sign()

        # buy
        self.auto.switch_to_window(0)
        self.driver.get(f"{self.config['app']['numi']}/nft/648728d4b0f2b854106cf579")
        time.sleep(5)
        self.auto.click("//div[contains(text(),'Buy for')]", 3)
        self.auto.click("//input[@type='checkbox']", 3)
        self.auto.click("//div[text('Buy for')]", 10)
        self.auto.confirm()

        logger.info(f"Incentive success")


if __name__ == '__main__':
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    list_tw_follow = AccountLoader(fp=f"{CODE_HOME}/twitter140.csv").parser_file()
    swap_params = {
        "account": list_account[6],
    }
    params = {
        "list_add": list_account,
    }
    try:
        vn = Numi(
            use_uc=True,
            params=params,
            list_tw_follow=list_tw_follow,
        )
        # vn.process_all(method="buy")
        vn.buy(**swap_params)
    except Exception as e:
        logger.error(e)
