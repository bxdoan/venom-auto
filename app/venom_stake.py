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
        "task": {
            "venom_foundation": "https://venom.network/tasks/venom-foundation",
            "venom_wallet": "https://venom.network/tasks/venom-wallet",
            "web3_world": "https://venom.network/tasks/web3-world",
            "venom_stake": "https://venom.network/tasks/venom-stake",
        },
        "app": {
            "venom_stake": "https://testnet.venomstake.com/",
        }
    },
}
VENOM_ADDRESS = "0:077873f1453fa67b0f1ce77f1e806675acd19c4694b9738be61fd406618f2f7a"


class VenomStake(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def stake(self, account: dict = None):

        self.driver.get(self.config['app']['venom_stake'])
        time.sleep(2)

        # setup metamask with seed phrase and password
        self.auto.switch_to_window(0)
        self.auto.walletSetup(account['seed_phrase'], account['password'])

        # click on the Connect Wallet button
        self.auto.switch_to_window(0)
        self.driver.refresh()
        time.sleep(8)
        self.auto.try_click("//div[contains(text(),'Connect Wallet')]", 3)
        self.auto.try_click("//div[contains(text(),'Venom Chrome')]", 3)
        self.auto.switch_to_window(-1)
        self.auto.try_click("//div[contains(text(),'Connect')]", 10)

        self.auto.switch_to_window(0)
        self.login_twitter(account)
        self.driver.close()

        # stake
        self.auto.switch_to_window(0)
        inputs = self.auto.try_find('//*[@id="app-wrapper"]/div[2]/div[3]/div/div/div[3]/div/div[2]/div[1]/input')
        inputs.send_keys('3')

        stake_buttons = self.auto.try_finds("//div[text()='Stake']")
        stake_buttons[2].click()
        time.sleep(2)

        self.auto.confirm()
        logger.info(f"Incentive success")


if __name__ == '__main__':
    # list_account = AccountLoader().parser_file()
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    swap_params = {
        "account": list_account[8],
    }
    params = {
        "list_add": list_account,
    }
    try:
        vn = VenomStake(
            use_uc=True,
            params=params
        )
        # vn.process_all(method="stake")
        vn.stake(**swap_params)
    except Exception as e:
        logger.error(e)
