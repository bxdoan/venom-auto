import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.config import get_logger, ACC_VENOM_PATH, CODE_HOME
from wallet import venom

logger = get_logger(__name__)


CONFIG = {
    "environment": "test",
    "mainnet": {
    },
    "test": {
        "app": {
            "ylide": "https://testnet.web3.world",
        }
    },
}


class Wallet(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def sent(self, account: dict = None):
        if not self.driver:
            self._try_start_driver(account)
        receiver = '0:e78ef3c0d28ec2081050f976afe35d60013e2dd91e749d1ea0e58a81f11820d0'
        self.driver.get(f"{self.config['app']['ylide']}")
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        self.auto.switch_to_window(0)
        self.driver.get(venom.POPUP_URL)
        time.sleep(3)

        balance = self.auto.try_find('//*[@id="root"]/div/div[1]/div[2]/div[1]/div/div[1]/div/div/div[2]')
        if balance:
            balance = balance.text.split(".")[0]
            logger.info(f"Balance: {balance}")
            if balance and int(balance) > 10:
                amount = int(balance) - 10
                self.auto.switch_to_window(0)
                self.auto.send(receiver=receiver, amount=amount)

        self.auto.switch_to_window(0)
        time.sleep(1)
        logger.info(f"Incentive success")
        self.driver.quit()


if __name__ == '__main__':
    fp = f"{CODE_HOME}/account.venomall.csv"
    list_account = AccountLoader(fp=fp).parser_file()
    swap_params = {
        "account": list_account[0],
    }
    params = {
        "list_add": list_account,
    }
    try:
        for account in list_account[21:]:
            vn = Wallet(params=params)
            vn.sent(**{
                "account": account,
            })
    except Exception as e:
        logger.error(e)
