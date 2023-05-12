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
            "web3_world": "https://testnet.web3.world",
        }
    },
}


class Web3World(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def swap(self, account: dict = None):
        amount     = self.params.get('amount', "0.01")
        from_token = self.params.get('from_token')
        to_token   = self.params.get('to_token')
        percent    = self.params.get('percent')

        self.driver.get(f"{self.config['app']['web3_world']}/swap")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(4)
        self.auto.try_click('//*[@id="root"]/div[1]/header/div/div[2]/div[2]/div/button', 2)
        self.auto.try_click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.try_click("//div[contains(text(),'Connect')]", 3)

        # swap
        self.auto.switch_to_window(0)
        inputs = self.auto.try_finds("//input")
        inputs[0].send_keys(amount)
        time.sleep(3)

        self.auto.click("//button[contains(text(),'Swap')]", 4)
        self.auto.click("//button[contains(text(),'Confirm')]", 4)
        self.auto.confirm()
        logger.info(f"Incentive success")


if __name__ == '__main__':
    # list_account = AccountLoader().parser_file()
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[0],
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
        # vn.process_all(method="swap")
        vn.swap(**swap_params)
    except Exception as e:
        logger.error(e)
