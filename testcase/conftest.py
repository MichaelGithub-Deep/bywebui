# Author : Michael Yang
# Date   : 10:02 am - 7/10/22
# File   : conftest.py

import pytest

from common import WebInit
from common import read_conf


@pytest.fixture(scope="function")
def GetDriver():
    CASE_TYPE = read_conf('CURRENCY').get('CASE_TYPE')
    if CASE_TYPE.lower() == 'web':
        driver = WebInit().enable
        yield driver
        driver.quit()
