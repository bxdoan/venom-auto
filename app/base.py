import shutil
import time
from datetime import datetime

from wallet import venom
from app import utils
from app.account import AccountLoader
from app.config import ACC_VENOM_PATH, HOME_TMP, ACC_FILE_NAME, CODE_HOME, get_logger
from app.enums import COLUMN_MAPPING, AccountStatus

logger = get_logger(__name__)


class BaseAuto(object):

    def __init__(self, **kwargs):
        self.list_account = []
        self.file_report = f"{HOME_TMP}/report_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        self.driver = None
        self.auto = None
        self.use_uc = kwargs.get('use_uc', True)
        self.params = kwargs.get('params', {})

        self.list_account = AccountLoader(fp=ACC_VENOM_PATH).parser_file()

        self.file_report = f"{HOME_TMP}/report_{ACC_FILE_NAME}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    def save_report(self, data: dict):
        list_index = list(COLUMN_MAPPING.values())

        format_data = []
        for k in list_index:
            value = data.get(k) if data.get(k) else ''
            format_data.append(value)

        utils.add_to_csv(self.file_report, format_data)

    def prepare_file_report(self):
        file_log_latest = utils.file_latest_in_path()
        if file_log_latest:
            index, row = utils.find_latest_row_index_log(file_log_latest)
            logger.info(f"Index: {index} - total account: {len(self.list_account)}")
            if index < len(self.list_account):
                # run not finish, use old file
                self.file_report = file_log_latest
                return index

        # prepare file report
        shutil.copyfile(f"{CODE_HOME}/account.sample.csv", self.file_report)
        return 0

    def process_all(self, method='deposit', **kwargs):
        method = getattr(self, method)
        if not method:
            raise Exception(f"Method {method} not found")

        # prepare list account
        index = self.prepare_file_report()
        list_account = self.list_account
        if index > 0:
            # continue from index in existing file report
            list_account = self.list_account[index:]

        for idx, account in enumerate(list_account):
            real_idx = idx + index
            logger.info(f"Request for account: {real_idx} - {account['address']}")

            if account.get('status') != AccountStatus.Inactive:
                # if account is active, run method
                try:
                    kwargs.update({
                        'account': account,
                    })
                    self.params.update({
                        'account_index': real_idx,
                    })
                    method(**kwargs)
                    account['status'] = AccountStatus.Inactive
                except Exception as e:
                    logger.error(e)

                self.driver.quit()
                self.driver = self.auto.launchSeleniumWebdriver(self.use_uc)
            else:
                logger.info(f"Account {account['address']} is inactive")

            self.save_report(account)

        logger.info(f'Request Success for account len: {len(list_account)}')
        logger.info(f"file report: {self.file_report}")

    def login_twitter(self, acc: dict) -> None:
        url = "https://twitter.com/i/flow/login"
        self.driver.execute_script("window.open('');")
        time.sleep(5)  # wait for the new window to open
        self.auto.switch_to_window(-1)
        self.driver.get(url)
        time.sleep(5)
        # fill in email
        twemail = self.auto.try_find('//input')
        twemail.send_keys(acc['tw_email'])
        self.auto.click('//span[text()="Next"]', 7)

        if acc['tw_fa']:
            logger.info('Login with 2FA')
            twpass_or_username = self.auto.try_finds('//input')
            twpass_or_username[1].send_keys(acc['tw_pass'])
            self.auto.click('//span[text()="Log in"]', 3)
            self.auto.click('//span[text()="Next"]', 2)

            input_totp = self.auto.try_find('//input')
            input_totp.send_keys(utils.totp(acc['tw_fa']))
            self.auto.try_click("//span[contains(text(), 'Next')]", 3)
            self.auto.try_click("//span[contains(text(), 'Skip for')]", 3)
        else:
            logger.info('Login with password')
            twpass_or_username = self.auto.try_finds('//input')
            if len(twpass_or_username) == 1:
                if "gmail" in acc['tw_email']:
                    username = acc['tw_email'].split('@')[0]
                else:
                    # email with last 3 char of address
                    username = f"{acc['tw_email'].split('@')[0]}{acc['address'][:-3]}"
                twpass_or_username[0].send_keys(username)
                self.auto.click('//span[text()="Next"]', 3)
                twpass = self.auto.try_finds('//input')
                twpass[1].send_keys(acc['tw_pass'])
                self.auto.click('//span[text()="Log in"]', 3)
            else:
                twpass_or_username[1].send_keys(acc['tw_pass'])
                self.auto.click('//span[text()="Next"]', 3)

        self.auto.switch_to_window(0)
        time.sleep(3)
        logger.info(f"Login twitter for account: {acc['tw_email']}")

    def login_discord(self, account: dict) -> None:
        token = account['dis_token']
        url = "https://discord.com/login"
        self.driver.execute_script("window.open('');")
        time.sleep(5)  # wait for the new window to open
        self.auto.switch_to_window(-1)
        self.driver.get(url)
        script = """
                function login(token) {
                setInterval(() => {
                document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
                }, 50);
                setTimeout(() => {
                location.reload();
                }, 2500);
                }   
                """
        if token:
            logger.info('Login with token')
            self.driver.execute_script(script + f'\nlogin("{token}")')
        else:
            logger.info('Login with password')
            twemail = self.auto.try_finds('//input')
            twemail[0].send_keys(account['dis_email'])
            twemail[1].send_keys(account['dis_pass'])
            self.auto.click('//div[text()="Log In"]', 8)

        time.sleep(5)
        self.auto.switch_to_window(0)
        logger.info(f"Login discord for account: {account['dis_email']}")

    def swap(self, account: dict = None):
        pass

    def addLiquidity(self, account: dict = None):
        pass

    def removeLiquidity(self, account: dict = None):
        pass

    def stake(self, account: dict = None):
        pass

    def unstake(self, account: dict = None):
        pass

    def harvest(self, account: dict = None):
        pass

    def claim(self, account: dict = None):
        pass

    def farm(self, account: dict = None):
        pass


class VenomAuto(BaseAuto):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto = venom
        self.driver = self.auto.launchSeleniumWebdriver(self.use_uc)
