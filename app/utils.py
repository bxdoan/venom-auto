import csv
import json
import openpyxl
import os
import pandas as pd
import random
import string

from app.config import HOME_PACKAGE, HOME_TMP


def read_xlsx_file(dir_file: str, column_mapping: dict = None, sheet_name: str = None) -> list:
    wb = openpyxl.load_workbook(dir_file)
    if not sheet_name:
        sheet_name = wb.sheetnames[0]
    ws = wb[sheet_name]  # the 1st sheet at index 0

    max_column = ws.max_column
    max_row = ws.max_row

    raw_headers = [ws.cell(row=1, column=ci).value for ci in range(1, max_column + 1)]  # ci aka column_index
    raw_headers = list(filter(None, raw_headers))  # remove None column out of header list

    v_fields = [h and column_mapping.get(h.strip()) for h in
                raw_headers]  # h aka header, ensure header is not null to strip and no error is thrown
    raw_v_rows = []  # raw_v_rows aka raw vehicle rows
    col_count = len(raw_headers)
    for ri in range(2, max_row + 1):  # ri aka row_index - we skip the 1st row which is the header rows
        values = [ws.cell(row=ri, column=ci).value for ci in range(1, col_count + 1)]  # ci aka column_index
        rvr = dict(zip(v_fields, values))  # rvr aka raw_vehicle_row
        raw_v_rows.append(rvr)
    return raw_v_rows


def read_csv_file(dir_file: str, column_mapping: dict = None) -> list:
    raw_v_rows = []  # raw_v_rows aka raw vehicle rows
    # region read csv
    csv.register_dialect('PARCEL_dialect',
                         delimiter=',',
                         quoting=csv.QUOTE_ALL,
                         skipinitialspace=True
                         )
    with open(dir_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, dialect='PARCEL_dialect')
        for row in csv_reader:
            r = dict()  # r aka record
            for key, value in column_mapping.items():
                r[value] = row.get(key)
            raw_v_rows.append(r)
    return raw_v_rows


def load_abi(file_name):
    fp = f'{HOME_PACKAGE}/{file_name}'
    with open(fp, 'r') as f:
        abi = json.load(f)
        return abi


def force2bool(input : str or bool) -> bool:
    if isinstance(input, bool):
        return input

    elif isinstance(input, str):

        if input.lower().strip() == 'true': return True
        if input.lower().strip() == 't':    return True
        if input.lower().strip() == 'True': return True
        if input.lower().strip() == 'T':    return True
        if input.lower().strip() == 'yes':  return True
        if input.lower().strip() == 'Yes':  return True
        if input.lower().strip() == 'y':    return True
        return False

    else:
        return False


def force_int(value, default=0):
    try:
        return int(value)
    except Exception as _e:
        return default


def force_float(value, default=0.0):
    try:
        return float(value)
    except Exception as _e:
        return default


def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def file_latest_in_path(log_dir: str = None) -> str:
    if log_dir is None:
        log_dir = HOME_TMP

    files = os.listdir(log_dir)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)))
    if len(files) == 0:
        return None
    return os.path.join(log_dir, files[-1])


def find_latest_row_index_log(file_report) -> tuple:
    df = pd.read_csv(file_report)
    # index last row
    index = df.index[-1]
    row = df.loc[index]
    return index, row


def refresh_ipadress():
    # Define the range of the IP address to choose from
    ip_range = ["192.168.1.", "10.0.0."]

    # Choose a random IP address
    new_ip = ip_range[random.randint(0, len(ip_range) - 1)] + str(random.randint(1, 254))

    # Define the subnet mask
    subnet_mask = "255.255.255.0"

    # Get the name of the current active network interface
    interface_name = os.popen(
        "networksetup -listallhardwareports | awk '/Wi-Fi|AirPort/{getline; print $2}'").read().strip()

    # Change the IP address and subnet mask using the networksetup command
    cmd = "sudo networksetup -setmanual \"" + interface_name + "\" " + new_ip + " " + subnet_mask
    print(cmd)
    os.system(cmd)


def df_to_csv(df, file_path):
    # Save dataframe as csv.
    df.to_csv(file_path, index=False)


def csv_to_df(file_path):
    # Read csv to dataframe.
    df = pd.read_csv(file_path)
    return df


def add_to_csv(file_path, add_text):
    # Add a line to file_name.csv
    # Should be like [xx,xx,xx]
    df = csv_to_df(file_path)
    l = len(df)
    df.loc[l] = add_text
    df_to_csv(df, file_path)