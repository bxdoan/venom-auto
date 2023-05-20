from dongle_tle_api import Dongle

from app import utils

if __name__ == '__main__':
    print(f"IP Address: {utils.ip()}")
    Dongle().reboot()
    utils.change_network()
