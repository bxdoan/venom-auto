import time

from app.account import AccountLoader
from app.base import VenomAuto
from app.chatgpt import tweet
from app.config import get_logger, ACC_VENOM_PATH, CODE_HOME, MAIN_INDEX

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
        base_url = "https://twitter.com/bxdoan/status/"
        list_status = [
            "1694173588264481198",
            "1694174113156542638",
            "1694174456024023334",
            "1694174771012149425",
            "1694174954429026487",
        ]

        self.driver.get(f"{base_url}{list_status[0]}")
        for status_id in list_status[1:]:
            url = f"{base_url}{status_id}"
            self.driver.execute_script("window.open('');")
            time.sleep(1)
            self.auto.switch_to_window(-1)
            self.driver.get(url)

        time.sleep(3)
        count = 0
        number_tab = len(self.driver.window_handles)
        while True:
            for i in range(number_tab):
                self.auto.switch_to_window(i)
                time.sleep(0.7)
                self.driver.refresh()

            count += 1
            logger.info(f"View {count} times")

        logger.info(f"Incentive success")


if __name__ == '__main__':
    list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()
    account_index = MAIN_INDEX
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
