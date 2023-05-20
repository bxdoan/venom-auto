import sys

from app import utils

if __name__ == '__main__':
    secret = sys.argv[1]
    otp = utils.totp(secret)
    print(otp)
