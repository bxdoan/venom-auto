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
            "oasis_gallery": "https://testnet.oasis.gallery",
        }
    },
}


class OasisGallery(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def buy(self, account: dict = None):

        self.driver.get(f"{self.config['app']['oasis_gallery']}/buy")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(4)
        self.auto.try_click('//*[@id="__next"]/div[1]/div[1]/div[2]/div[3]/button', 2)
        self.auto.try_click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.try_click("//div[contains(text(),'Connect')]", 3)

        # swap
        self.auto.switch_to_window(0)
        inputs = self.auto.try_finds("//span[contains(text(),'Buy now')]")
        inputs[0].click()
        time.sleep(3)

        self.auto.click("//button[contains(text(),'Confirm')]", 4)
        self.auto.confirm(account['password'])
        time.sleep(20)
        logger.info(f"Incentive success")

    def list(self, account: dict = None):
        self.driver.get(f"{self.config['app']['oasis_gallery']}/buy")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(4)
        self.auto.try_click('//*[@id="__next"]/div[1]/div[1]/div[2]/div[3]/button', 2)
        self.auto.try_click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.try_click("//div[contains(text(),'Connect')]", 3)

        # swap
        self.auto.switch_to_window(0)
        self.driver.get(f"{self.config['app']['oasis_gallery']}/profile/{account['address']}")
        time.sleep(4)
        self.auto.click('//*[@id="__next"]/div[1]/div[3]/div[2]/div[2]/a/div/div[1]/div', 4)
        self.auto.click('//*[@id="__next"]/div[1]/div[2]/div/div[3]/div/div/div[2]/div[2]/button', 4)

        inputs = self.auto.try_finds("//input[@placeholder='Amount']")
        inputs[0].send_keys("5")
        time.sleep(2)
        self.auto.click('//*[@id="__next"]/div[2]/div[2]/div/div/div[5]/button', 4)
        self.auto.confirm(account['password'])
        time.sleep(45)
        logger.info(f"Incentive success")


if __name__ == '__main__':
    # list_account = AccountLoader().parser_file()
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[44],
    }
    params = {
        "list_add": list_account,
        "amount": "1",
        "from_token": "VENOM",
        "to_token": "USDT",
    }
    try:
        vn = OasisGallery(
            use_uc=True,
            params=params
        )
        vn.process_all(method="list")
        # vn.buy(**swap_params)
        # vn.list(**swap_params)
    except Exception as e:
        logger.error(e)
