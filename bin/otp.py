import base64
import hmac
import sys
import time


def totp(secret: str) -> str:
    """ Calculate TOTP using time and key """
    key = base64.b32decode(secret, True)
    now = int(time.time() // 30)
    msg = now.to_bytes(8, "big")
    digest = hmac.new(key, msg, "sha1").digest()
    offset = digest[19] & 0xF
    code = digest[offset : offset + 4]
    code = int.from_bytes(code, "big") & 0x7FFFFFFF
    code = code % 1000000
    return "{:06d}".format(code)


if __name__ == '__main__':
    secret = sys.argv[1]
    otp = totp(secret)
    print(otp)
