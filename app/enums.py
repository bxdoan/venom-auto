from enum import Enum, EnumMeta

FOLLOW_XP = "//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div/span/span"


class EnumDirectValueMeta(EnumMeta):
    def __getattribute__(cls, name):
        value = super().__getattribute__(name)
        if isinstance(value, cls):
            value = value.value
        return value


class BaseEnum(Enum, metaclass=EnumDirectValueMeta):
    @classmethod
    def all(cls, except_list=None):
        if except_list is None:
            except_list = []
        return [c.value for c in cls if c.value not in except_list]

    @classmethod
    def keys(cls):
        return [k.name for k in cls]

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def all_element_index(cls, index):
        # check element is list and len
        first_element = cls.all()[0]
        if type(first_element) in (list, tuple):
            if index > len(first_element) - 1:
                return []

        e = []
        for c in cls.all():
            e.append(c[index])

        return e


class AccountStatus(BaseEnum):
    Active = '0'
    Inactive = '1'


class GasPrice(BaseEnum):
    Low = 'Low'
    Average = 'Average'
    High = 'High'


COLUMN_MAPPING = {
    'Name': 'name',
    'Address': 'address',
    'Private Key': 'private_key',
    "Seed Phrase": 'seed_phrase',
    "Password": 'password',
    "Status": 'status',
    "Balance": 'balance',
    "TWACC": 'tw_acc',
    "TWPASS": 'tw_pass',
    "TWFA": 'tw_fa',
    "TWEMAIL": 'tw_email',
    "DISEMAIL": 'dis_email',
    "DISPASS": 'dis_pass',
    "DISTOKEN": 'dis_token',
    "TWFAB": 'tw_fab',
    'Description': 'description',
}
