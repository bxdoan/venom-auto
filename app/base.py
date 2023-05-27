import shutil
import time
from datetime import datetime

from wallet import venom
from app import utils
from app.account import AccountLoader
from app.config import ACC_VENOM_PATH, HOME_TMP, ACC_FILE_NAME, CODE_HOME, get_logger, CHANGE_NETWORK, LIST_FOLLOW
from app.enums import COLUMN_MAPPING, AccountStatus, FOLLOW_XP
from app.chatgpt import tweet

logger = get_logger(__name__)


class BaseAuto(object):

    def __init__(self, **kwargs):
        self.list_account = []
        self.file_report = f"{HOME_TMP}/report_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        self.use_uc = kwargs.get('use_uc', True)
        self.driver = None
        self.auto = None
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
        logger.info(f"Save report: {format_data}")

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

        create_driver = True
        for idx, account in enumerate(list_account):
            if create_driver:
                self._try_start_driver(account)

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
                create_driver = True
            else:
                logger.info(f"Account {account['address']} is inactive")
                create_driver = False

            self.save_report(account)
            self._change_proxy()

        logger.info(f'Request Success for account len: {len(list_account)}')
        logger.info(f"file report: {self.file_report}")

    def _try_start_driver(self, account):
        while True:
            try:
                self.driver = self.auto.launchSeleniumWebdriver(address=account['address'])
                if self.driver:
                    break
            except Exception as e:
                logger.error(f"An error occurred: {e}, retrying in 10 seconds.")
                time.sleep(10)

    def _change_proxy(self):
        if utils.force2bool(CHANGE_NETWORK):
            utils.change_network()

    def _tweet(self) -> None:
        self.auto.switch_to_window(0)
        self.auto.open_new_tab("https://twitter.com/compose/tweet")
        time.sleep(3)
        self.auto.try_click("//span[contains(text(),'Maybe later')]", 4)
        self.auto.try_click("//div[@aria-label='Tweet text']", 2)
        message = tweet().replace('"', '')
        self.auto.try_send_keys("//div[@aria-label='Tweet text']", f"{message}\n")
        self.auto.try_click("//span[text()='Tweet']", 10)
        self.auto.try_click("//span[contains(text(),'Got it')]", 5)
        logger.info(f"Tweet: {message}")
        self.driver.close()

    def _follow_list(self, account: dict = None) -> None:
        list_fl = LIST_FOLLOW.split(',')
        list_fl = [int(x) for x in list_fl]
        for fl in list_fl:
            self._follow(account, fl)

    def _follow(self, account: dict = None, index_user : int = None) -> None:
        if not index_user:
            return
        self.auto.switch_to_window(0)
        username = self.list_account[index_user]['tw_acc']
        if username != account['tw_acc']:
            url = f"https://twitter.com/intent/user?screen_name={username}"
            self.auto.open_new_tab(url)
            self.auto.try_click(FOLLOW_XP, 10)
        self.driver.close()
        logger.info(f"Follow: {username}")

    def _get_2fa(self, account: dict):
        if account.get('tw_fa'):
            return
        self.auto.switch_to_window(0)
        url_2fa = "https://twitter.com/i/flow/two-factor-auth-app-enrollment"
        self.auto.open_new_tab(url_2fa)
        time.sleep(7)
        self.auto.try_click("//span[contains(text(), 'Get start')]", 5)
        self.auto.try_click("//span[contains(text(), 't scan the QR code')]", 3)

        text_fa = self.auto.try_find('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/span').text
        logger.info(f"2fa text: {text_fa}")
        account['tw_fa'] = text_fa
        self.auto.try_click("//span[contains(text(), 'Next')]", 5)
        otp = utils.totp(text_fa)
        otp_input = self.auto.try_find('//input')
        otp_input.send_keys(otp)
        self.auto.try_click("//span[contains(text(), 'Confirm')]", 5)

        text_b = self.auto.try_find('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div/div/div[2]/div[1]/div[2]/span/span/span').text
        text_fa_backup = utils.get_fa_backup(text_b)
        logger.info(f"2fa backup text: {text_fa_backup}")
        account['tw_fab'] = text_fa_backup
        self.auto.try_click("//span[contains(text(), 'Done')]", 5)

        self.auto.try_click("//span[contains(text(), 'Get start')]", 7)
        self.auto.try_click("//span[contains(text(), 'Got it')]", 7)
        logger.info("Get 2fa successfully")

    def login_twitter(self, acc: dict) -> None:
        url = "https://twitter.com/i/flow/login"
        self.auto.open_new_tab(url)
        time.sleep(9)
        # fill in email
        twemail_or_twacc = self.auto.try_find('//input')

        if acc['tw_fa']:
            logger.info(f"Login with 2FA {acc['tw_acc']}")
            twemail_or_twacc.send_keys(acc['tw_acc'])
            self.auto.try_click('//span[text()="Next"]', 6)
            twpass_or_username = self.auto.try_finds('//input')
            twpass_or_username[1].send_keys(acc['tw_pass'])
            self.auto.try_click('//span[text()="Log in"]', 6)
            self.auto.try_click('//span[text()="Next"]', 6)

            input_totp = self.auto.try_find('//input')
            input_totp.send_keys(utils.totp(acc['tw_fa']))
            self.auto.try_click("//span[contains(text(), 'Next')]", 10)
            input_submit = self.auto.try_find("//input[@type='submit']")
            if input_submit:
                input_submit.click()
                time.sleep(10)
                self.auto.try_click("//input[@type='submit']", 8)

            self.auto.try_click("//span[contains(text(), 'Skip for')]", 3)
        else:
            logger.info('Login with password')
            twemail_or_twacc.send_keys(acc['tw_email'])
            self.auto.click('//span[text()="Next"]', 7)
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
                self.auto.try_click('//span[text()="Log in"]', 3)
                self.auto.try_click('//span[text()="Next"]', 3)

        time.sleep(3)
        logger.info(f"Login twitter for account: {acc['tw_email']}")

    def login_discord(self, account: dict) -> None:
        token = account['dis_token']
        self.auto.open_new_tab("https://discord.com/channels/@me")
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

        time.sleep(10)
        logger.info(f"Login discord for account: {account['dis_email']}")

    def _check_logged_in_twitter(self):
        self.auto.open_new_tab("https://twitter.com/home")
        time.sleep(8)
        logged_in_twitter = False
        if not self.auto.try_find("//span[contains(text(),'Sign in to Twitter')]"):
            logged_in_twitter = True

        self.driver.close()
        self.auto.switch_to_window(0)
        return logged_in_twitter

    def _check_logged_in_discord(self):
        self.auto.open_new_tab("https://discord.com/channels/@me")
        time.sleep(8)
        logged_in_discord = False
        if not self.auto.try_find("//div[contains(text(),'re so excited to see you again')]"):
            logged_in_discord = True

        self.driver.close()
        self.auto.switch_to_window(0)
        return logged_in_discord

    def _daily_faucet(self, account: dict = None):
        try:
            url = f"https://venom.network/faucet"
            self.auto.switch_to_window(-1)
            self.driver.get(url)
            time.sleep(5)
            answer = self.params.get('answer')
            self.auto.try_click("//a[contains(text(), 'Start')]", 3)
            self.auto.try_click(f"//span[contains(text(), '{answer}')]", 3)
            self.auto.try_click("//button[contains(text(), 'Send')]", 7)
            self.auto.try_click("//span[contains(text(), 'Claim')]", 3)
            self.auto.sign()
            time.sleep(15)
            logger.info(f"Faucet claim successfull for {account['address']}")
        except Exception as e:
            logger.error(e)

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
        self.use_uc = kwargs.get('use_uc', True)
        self.auto = venom

    def _daily_faucet(self, account: dict = None):
        try:
            url = f"https://venom.network/faucet"
            self.auto.switch_to_window(-1)
            self.driver.get(url)
            time.sleep(10)
            answer = self.params.get('answer')
            self.auto.try_click("//a[contains(text(), 'Start')]", 3)
            self.auto.try_click(f"//span[contains(text(), '{answer}')]", 3)
            self.auto.try_click("//button[contains(text(), 'Send')]", 7)
            self.auto.try_click("//span[contains(text(), 'Claim')]", 3)
            self.auto.sign()
            time.sleep(15)
            logger.info(f"Faucet claim successfull for {account['address']}")
        except Exception as e:
            logger.error(e)

    def _connect_wallet(self):
        self.driver.refresh()
        time.sleep(7)
        connect_wallet = self.auto.try_find("//h1[contains(text(),'Complete three tasks and')]")
        if connect_wallet:
            self.auto.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[2]/span', 2)
            self.auto.click("//div[contains(text(),'Venom Chrome')]", 3)
            self.auto.switch_to_window(-1)
            self.auto.click("//div[contains(text(),'Connect')]", 3)

    def _check_logged_in_wallet(self):
        self.auto.open_new_tab(venom.POPUP_URL)
        logged_in_wallet = False
        if self.auto.try_find("//p[contains(text(),'Account 1')]"):
            logged_in_wallet = True
        self.driver.close()
        self.auto.switch_to_window(0)
        logger.info(f"Logged in wallet: {logged_in_wallet}")
        return logged_in_wallet
