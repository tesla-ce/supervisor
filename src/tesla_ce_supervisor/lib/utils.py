from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.lib.tesla.conf import Config


def to_list(x):
    if type(x) is tuple:
        return [to_list(y) for y in x]
    else:
        return x

def to_tuple(x):
    if type(x) is list:
        return tuple([to_tuple(y) for y in x])
    else:
        return x

def utils_get_config():
    client = TeslaClient()
    client.get_config_path()
    client.load_configuration()
    return client.get_config()