from os import getenv
from dotenv import load_dotenv


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


load_dotenv(override=False)

LOG_LEVEL = getenv(key="LOG_LEVEL", default="WARN").upper()

AIMS_SAAS_URL = getenv(
    key="AIMS_SAAS_URL", default="https://stage00.common.solumesl.com/common"
)
AIMS_SAAS_USERNAME = getenv(key="AIMS_SAAS_USERNAME")
AIMS_SAAS_PASSWORD = getenv(key="AIMS_SAAS_PASSWORD")
AIMS_SAAS_COMPANY = getenv(key="AIMS_SAAS_COMPANY", default="KIM")

TIMEOUT = 30

VERIFY_SSL = strtobool(getenv(key="VERIFY_SSL", default="true"))
