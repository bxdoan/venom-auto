import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.chatgpt import tweet
from app.config import get_logger, ACC_VENOM_PATH, CODE_HOME

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


class X(VenomAuto):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list_tw_follow = kwargs.get('list_tw_follow') or []

        self.environment = CONFIG['environment']
        self.config = CONFIG[self.environment]

    def view(self, account: dict = None):
        if not self.driver:
            self._try_start_driver(account)
        url = "https://twitter.com/bxdoan/status/1693844113987395905"
        self.driver.get(url)
        time.sleep(3)
        count = 0
        while True:
            self.driver.refresh()
            time.sleep(4)
            count += 1
            logger.info(f"View {count} times")

        logger.info(f"Incentive success")


if __name__ == '__main__':
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    account_index = 1
    swap_params = {
        "account": list_account[account_index],
    }
    params = {
        "list_add": list_account,
        # 'account_index': account_index,
    }
    try:
        vn = X(
            use_uc=True,
            params=params,
        )
        # vn.process_all(method="view")
        vn.view(**swap_params)
    except Exception as e:
        logger.error(e)
