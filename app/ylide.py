import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.chatgpt import tweet
from app.config import get_logger, ACC_VENOM_PATH, CODE_HOME, EXTENSION_ID

logger = get_logger(__name__)


CONFIG = {
    "environment": "test",
    "mainnet": {
    },
    "test": {
        "app": {
            "ylide": "https://hub.ylide.io/feed/venom",
        }
    },
}


class Ylide(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list_tw_follow = kwargs.get('list_tw_follow') or []

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def buy(self, account: dict = None):
        if not self.driver:
            self._try_start_driver(account)

        self.driver.get(f"{self.config['app']['ylide']}")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        logged_in_twitter = self._check_logged_in_twitter()
        if not logged_in_twitter:
            self.login_twitter(account)
            self.driver.close()

        self._follow(account=account, user_name="@GradyDuane19821")
        self._follow(account=account, user_name="BrainBarrows")
        self._follow(account=account, user_name="HoytGerlach")
        self._follow(account=account, user_name="LailaFriesen")
        # self._tweet()
        # self._follow_list(account=account, list_acc=self.list_tw_follow)

        self.auto.switch_to_window(0)
        self._reload_extension()

        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(10)
        self.auto.click("//div[contains(text(),'Connect account')]", 3)

        self.auto.switch_to_window(0)
        self.auto.click("//div[contains(text(),'Venom Wallet')]", 4)
        self.auto.switch_to_window(-1)
        self.auto.click("//div[contains(text(),'Connect')]", 4)
        self.auto.switch_to_window(0)
        self.auto.click('//div[text()="Sign"]', 4)
        self.auto.sign(5)
        self.auto.confirm(time_to_sleep=60)

        # sign up
        self.auto.switch_to_window(0)
        self.auto.try_click('//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div[4]/textarea', 3)
        message = tweet().replace('"', '')
        self.auto.try_send_keys('//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div[4]/textarea', f"{message}\n")
        self.auto.click("//span[contains(text(),'Send via')]", 5)
        self.auto.confirm()

        logger.info(f"Incentive success")


if __name__ == '__main__':
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    list_tw_follow = AccountLoader(fp=f"{CODE_HOME}/twitter140.csv").parser_file()
    account_index = 3
    swap_params = {
        "account": list_account[account_index],
    }
    params = {
        "list_add": list_account,
        # 'account_index': account_index,
    }
    try:
        vn = Ylide(
            use_uc=True,
            params=params,
            list_tw_follow=list_tw_follow,
        )
        vn.process_all(method="buy")
        # vn.buy(**swap_params)
    except Exception as e:
        logger.error(e)
