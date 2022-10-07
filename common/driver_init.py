# Author : Michael Yang
# Date   : 8:40 pm - 5/10/22
# File   : driver_init.py
import sys
from typing import TypeVar

from selenium.common.exceptions import SessionNotCreatedException

sys.path.append('../')
import os, time
import requests

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from common.common import ErrorException, logger, read_conf
from config import WIN_CHROMEDRIVER, LINUX_CHROMEDRIVER, MAC_CHROMEDRIVER
from config import WIN_FIREFOXDRIVER, LINUX_FIREFOXDRIVER, MAC_FIREFOXDRIVER
from config import IE_PATH
from config import LOG_DIR

DAY = time.strftime("%Y-%m-%d", time.localtime(time.time()))

T = TypeVar('T')

# read the configuration params
WEB_UI = read_conf('WEB_UI')
URL = WEB_UI.get('WEB_URL')
BROWSER_NAME = WEB_UI.get('WEB_BROWSER')
WEB_HUB_HOST = WEB_UI.get('WEB_HUB_HOST')
WEB_IS_COLONY = WEB_UI.get('WEB_IS_COLONY')


def if_linux_firefox() -> bool:
    """
    needs some special handle when the system is linux and browser is firefox
    :browsername name of browser
    :return:
    """
    # 如果不是集群 并且linx firfox
    if WEB_IS_COLONY == False and sys.platform.lower() == 'linux' and BROWSER_NAME.lower() == 'firefox':

        return True

    else:
        return False


class WebInit:
    """
    return browser driver
    """

    def __init__(self):
        self.browser = BROWSER_NAME.lower()
        self.baseurl = URL

    @staticmethod
    def inspect_url_code(url: str) -> bool:
        """
        check if the url is available
        """
        try:
            rep = requests.get(url, timeout=10)  # timeout: 10s
            code = rep.status_code
            if code == 200:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f'url: {url} is not available. error: {e}')

    @property
    def url(self) -> str:
        return self.baseurl

    @url.setter
    def url(self, value: str) -> str or None:
        self.baseurl = value

    @property
    def linux_firefox_args(self) -> T:
        """
        linux os firefox browser parameter
        :return:
        """
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1200x600')
        return options

    @property
    def linux_chrome_args(self) -> T:
        """
        linux os chrome browser parameter
        :return:
        """
        option = webdriver.ChromeOptions()
        option.add_argument('--no-sandbox')  # no sandbox
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--headless')  # chrome does not supply UI page in Linux
        # so it has to add the headless option
        option.add_argument('--disable-gpu')  # it is mentioned in google doc
        option.add_argument('window-size=1920x1080')  # set screen resolution
        return option

    @property
    def enable(self) -> T:
        """
        use cluster mode to start the driver when WEB_IS_COLONY is enabled
        :return:
        """
        if WEB_IS_COLONY:
            return self.setups()
        else:
            return self.setup()

    def browser_setup_args(self, driver: T) -> T:
        """
        setting params for standalone browser
        :param driver: driver launches browser
        :return:
        """
        driver.maximize_window()
        driver.get(self.url)
        return driver

    def browaer_setups_args(self, descap: str, option=None) -> T:
        """
        setting params for cluster mode of browser
        :param descap: launch params
        :param option: params of browser
        :return:
        """
        driver = webdriver.Remote(command_executor='http://' + WEB_HUB_HOST + '/wd/hub',
                                  desired_capabilities=descap, options=option)
        driver.find_element()
        driver.maximize_window()
        driver.get(self.url)
        return driver

    def setup(self) -> T:
        """
        set the browser for standalone
        :return:
        """
        try:
            # system type
            if self.inspect_url_code(self.url):  # if the url is available
                current_sys = sys.platform.lower()
                log_path = os.path.join(LOG_DIR, f'{DAY}firefox.log')

                if current_sys == 'linux':  # linux

                    if self.browser == 'chrome':  # chrome
                        option = self.linux_chrome_args
                        driver = webdriver.Chrome(executable_path=LINUX_CHROMEDRIVER, options=option)
                        return self.browaer_setup_args(driver)

                    elif self.browser == 'firefox':  # firefox
                        options = self.linux_firefox_args
                        driver = webdriver.Firefox(executable_path=LINUX_FIREFOXDRIVER, options=options,
                                                   service_log_path=log_path)
                        drivers = self.browaer_setup_args(driver)
                        return drivers  # depends on Display when launch the firefox in Linux system

                    else:
                        logger.error(f'linux does not support this browser: {self.browser}')

                elif current_sys == 'darwin':  # mac

                    if self.browser == 'chrome':

                        driver = webdriver.Chrome(executable_path=MAC_CHROMEDRIVER)
                        return self.browser_setup_args(driver)

                    elif self.browser == 'firefox':
                        driver = webdriver.Firefox(executable_path=MAC_FIREFOXDRIVER, service_log_path=log_path)
                        return self.browser_setup_args(driver)

                    elif self.browser == 'safari':
                        driver = webdriver.Safari()
                        return self.browser_setup_args(driver)
                    else:
                        logger.error(f'mac does not support this browser: {self.browser}')

                elif current_sys == 'win32':

                    if self.browser == 'ie':
                        logger.warning('Please make sure that IE browser is installed !!!')
                        driver = webdriver.Ie(executable_path=IE_PATH)
                        return self.browser_setup_args(driver)

                    if self.browser == 'chrome':
                        driver = webdriver.Chrome(executable_path=WIN_CHROMEDRIVER)
                        return self.browser_setup_args(driver)

                    elif self.browser == 'firefox':
                        driver = webdriver.Firefox(executable_path=WIN_FIREFOXDRIVER, service_log_path=log_path)
                        return self.browser_setup_args(driver, )

                    else:
                        logger.error(f'windows does not support this browser: {self.browser}')

                else:
                    logger.error(f'current system: {current_sys} is not supported yet！')

            else:
                logger.error(f'url: {self.url} is not available！！！')

        except SessionNotCreatedException:
            logger.error('the current browser version and driver do not match, pls update the driver or chrome')

    def setups(self) -> T:
        """
        set the browser driver for cluster mode
        :return:
        """
        current_sys = sys.platform.lower()
        try:
            if self.inspect_url_code(self.url) and self.inspect_url_code('http://' + WEB_HUB_HOST):  # if the url and cluster host are available
                if current_sys == 'linux':  # linux
                    if self.browser == 'chrome':
                        option = self.linux_chrome_args
                        descap = DesiredCapabilities.CHROME
                        return self.browaer_setups_args(descap, option=option)

                    elif self.browser == 'firefox':
                        options = self.linux_firefox_args
                        descap = DesiredCapabilities.FIREFOX
                        return self.browaer_setups_args(descap, option=options)
                    else:
                        logger.error(f'linux does not support this browser: {self.browser}')

                elif current_sys == 'darwin':  # mac
                    if self.browser == 'safari':
                        descap = DesiredCapabilities.SAFARI
                        return self.browaer_setups_args(descap)

                    elif self.browser == 'chrome':
                        descap = DesiredCapabilities.CHROME
                        return self.browaer_setups_args(descap)

                    elif self.browser == 'firefox':
                        descap = DesiredCapabilities.FIREFOX
                        return self.browaer_setups_args(descap)

                    else:
                        logger.error('mac does not support this browser: {self.browser}')

                elif current_sys == 'win32':
                    if self.browser == 'ie':
                        descap = DesiredCapabilities.INTERNETEXPLORER
                        return self.browaer_setups_args(descap)

                    if self.browser == 'chrome':
                        descap = DesiredCapabilities.CHROME
                        return self.browaer_setups_args(descap)

                    elif self.browser == 'firefox':
                        descap = DesiredCapabilities.FIREFOX
                        return self.browaer_setups_args(descap)

                    else:
                        logger.error('windows does not support this browser: {self.browser}')

                else:
                    logger.error(f'current system: {current_sys} is not supported yet！')

            else:
                logger.error(f'url: {self.url} or cluster host: {WEB_HUB_HOST} is not available！！！')

        except SessionNotCreatedException:
            logger.error('the current browser version and driver do not match, pls update the driver or chrome')