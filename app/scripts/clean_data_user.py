# Desc: Tweet 20 words from the GPT-3.5 model
import os
import shutil

from app.account import AccountLoader
from app.config import ALL_USER_DATA_DIR, CODE_HOME
from app import utils


if __name__ == '__main__':
    dir_name = '049d583a4428d3567541a094de4293e02eb6f2d26ae281583c20357a4f66973f'
    fp = "account.venom_dietwt.csv"
    list_faucet_acc = AccountLoader(fp=f"{CODE_HOME}/{fp}").parser_file()
    for a in list_faucet_acc:
        # check dir is exists
        target_dir = os.path.join(ALL_USER_DATA_DIR, utils.cook_address(a['address']))
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            shutil.rmtree(target_dir)

