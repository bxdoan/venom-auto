from dongle_tle_api import Dongle
import requests

if __name__ == '__main__':
    ip_address_now = requests.get('https://checkip.amazonaws.com').text.strip()
    print(f"IP Address: {ip_address_now}")
    Dongle().reboot()
