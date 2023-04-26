import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
CODE_HOME = os.path.abspath(os.path.dirname(__file__) + '/..')
HOME_PACKAGE = os.path.abspath(os.path.dirname(__file__) + '/package')

HOME_TMP = f'{CODE_HOME}/tmp'
HOME_LOG = f'{CODE_HOME}/log'
list_make_dir = [
    HOME_TMP, HOME_LOG
]
for _dir in list_make_dir:
    # make sure the folder exists before using it
    os.makedirs(_dir, exist_ok=True)

ACC_PATH = os.environ.get('ACC_PATH')
ACC_SEI_PATH = os.environ.get('ACC_SEI_PATH')
try:
    ACC_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.environ.get('ACC_PATH'))
    ACC_SEI_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.environ.get('ACC_SEI_PATH'))
except Exception as e:
    print(f"{ACC_PATH=} and {ACC_SEI_PATH} Error: {e}")

ACC_SEI = ACC_SEI_PATH.split('/')[-1].replace('.csv', '')
WAIT_TIME = os.environ.get('WAIT_TIME')
PASSWORD = os.environ.get('PASSWORD')  # password default for all accounts

HEADLESS = os.environ.get('HEADLESS')     # for headless mode chrome
WIDTH    = os.environ.get('WIDTH', 1300)  # for which width of chrome
HEIGHT   = os.environ.get('HEIGHT', 1020) # for which height of chrome

# download the newest version of keplr extension from:
# ref. https://chrome.google.com/webstore/detail/keplr/dmkamcknogkgcdfhhbddcghachkejeap
# or from  https://github.com/chainapsis/keplr-wallet
# or get from your local machine
# /Users/$USER/Library/Application\ Support/Google/Chrome/Default/Extensions/
EXTENSION_DIR      = os.environ.get('EXTENSION_DIR')
EXTENSION_ID_KEPLR = os.environ.get('EXTENSION_ID_KEPLR')
EXTENSION_DIR_LEAP = os.environ.get('EXTENSION_DIR_LEAP')
EXTENSION_ID_LEAP  = os.environ.get('EXTENSION_ID_LEAP')
DRIVER_PATH        = os.environ.get('DRIVER_PATH')


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel("DEBUG")

    # Create handlers
    c_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    # Configure the logger
    simple_format = logging.Formatter(
        "%(asctime)s [%(funcName)s() +%(lineno)d]: %(levelname)-8s %(message)s",
        datefmt="%b-%d %H:%M:%S%Z"
    )
    c_handler.setFormatter(simple_format)

    # Add handlers to the logger
    log.addHandler(c_handler)

    return log


# Use this variable for global project
logger = get_logger(__name__)
