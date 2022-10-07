# Author : Michael Yang
# Date   : 9:18 pm - 5/10/22
# File   : web_base.py

import os
import sys
import time
from enum import Enum
from typing import TypeVar

import allure
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from config import RESULT_SCREEN_DIR
from common.common import ErrorException, logger, is_assertion, read_conf
from common.read_data import GetCaseYaml, replace_py_yaml

EM = TypeVar('EM')  # any type

# 读取配置参数
WEB_UI = read_conf('WEB_UI')
WEB_POLL_FREQUENCY = WEB_UI.get('WEB_IMPLICITLY_WAIT_TIME')
WEB_IMPLICITLY_WAIT_TIME = WEB_UI.get('WEB_POLL_FREQUENCY')

# 读取 项目类型
CASE_TYPE = read_conf('CURRENCY').get('CASE_TYPE')

if CASE_TYPE.lower() == 'web':
    POLL_FREQUENCY = WEB_POLL_FREQUENCY
    IMPLICITLY_WAIT_TIME = WEB_IMPLICITLY_WAIT_TIME


class Locate(Enum):
    """
    locate class
        locate type
            correspond operations of selenium
            function is the function type in web 8
          types                              selenium
          (/ respect link_text or link > LINK_TEXT)
          "id"                            >   ID
          "xpath"                         >   XPATH
          "link_text/link"                >   LINK_TEXT
          "partial_link_text/partial"     >   PARTIAL_LINK_TEXT
          "name"                          >   NAME
          "tag_name/tag"                  >   TAG_NAME
          "class_name/class"              >   CLASS_NAME
          "css_selector/css"              >   CSS_SELECTOR
          "function"                      >   web_html_content or web_url web_title
    """
    web_types = ['id', 'xpath', 'link_text', 'link', 'partial_link_text', 'partial', 'name', 'tag_name',
                 'tag', 'class_name', 'class', 'css_selector', 'css', 'function']


class Operation(Enum):
    """
       operation type:
       type                                        action
       input                       >               type in
       click                       >               click the element
       text                        >               text
       submit                      >               submit form
       scroll                      >               scroll and slide down
       clear                       >               clear the content of input
       jsclear                     >               js clear
       jsclear_continue_input      >               clear js and then input
       clear_continue_input        >               clear and then input
       web_url                     >               get the current url
       web_title                   >               get the current title
       web_html_content            >               the html content
       iframe                      >               change the frame

       slide                       >               slide screen
       """

    web_operation = ['input', 'click', 'text', 'submit', 'scroll', 'clear',
                     'jsclear', 'jsclear_continue_input', 'clear_continue_input',
                     'web_url', 'web_title', 'web_html_content', 'iframe']


class Base:

    def __init__(self, driver):
        self.driver = driver

    def web_by(self, types: str) -> EM or None:
        """
        get locate type
        :param types:  str  in(id,xpath,link_text/link,partial_link_text/partial,name,
        tag_name/tag,class_name/class,css_selector/css)
        :return:
        """
        types = types.lower()
        locate_types = Locate.web_types.value

        if types not in locate_types:
            logger.error(f'web only support {locate_types}')
            raise ErrorException(f'operation type {types} is not supported yet')

        if types == "id":
            return By.ID
        elif types == "xpath":
            return By.XPATH
        elif types == "link_text" or types == "link":
            return By.LINK_TEXT
        elif types == "partial_link_text" or types == "partial":
            return By.PARTIAL_LINK_TEXT
        elif types == "name":
            return By.NAME
        elif types == "tag_name" or types == "tag":
            return By.TAG_NAME
        elif types == "class_name" or types == "class":
            return By.CLASS_NAME
        elif types == "css" or types == "css_selector":
            return By.CSS_SELECTOR
        elif types == "function":
            return types

        else:
            logger.error(f"web only support {locate_types}")
            raise Exception(f'operation type {types} is not supported yet')

    def get_by_type(self, types: str) -> EM or None:
        """
        APP or WEB  reserved for expanding
        :param types:   定位类型
        :return:
        """
        if CASE_TYPE.lower() == 'web':
            return self.web_by(types)

    @property
    def web_title(self):
        """
        get the current title
        :return:
        """
        title = self.driver.title
        logger.debug(f"get current title {title}")
        return title

    @property
    def web_url(self):
        """
        get the current url
        :return:
        """
        url = self.driver.current_url
        logger.debug(f"get current url {url}")
        return url

    @property
    def web_html_content(self):
        """
        get html content
        :return:
        """
        content = self.driver.page_source
        logger.debug('get current page content')
        return content

    def sleep(self, s: float) -> float or int:
        """
        sleep: s
        :param s:
        :return:
        """
        if s:
            logger.debug('sleep: {} /s'.format(s))
            time.sleep(s)
        else:
            pass

    def web_refresh(self):
        """
        refresh current page
        :return:
        """
        logger.debug('refresh current page')
        return self.driver.refresh()

    def web_back(self):
        """
        back to last page
        :return:
        """
        logger.debug('back to last page')
        return self.driver.back()

    def web_forward(self):
        """
        jump to next page
        :return:
        """
        logger.debug('jump to next page')
        return self.driver.forward()

    def web_click(self):
        """
        click the current page
        :return:
        """

        base_click = self.driver.click()
        logger.debug('click the current page')
        return base_click

    def web_scroll(self, direction: str) -> None:
        """
        page scroll, try to use web_scroll_to_ele if it does not work in some pages
        :param direction: str :  up or Down
        :return:
        """
        if direction == "up":
            logger.debug('scroll to top')
            self.driver.execute_script("window.scrollBy(0, -10000);")
        if direction == "down":
            logger.debug('scroll to bottom')
            self.driver.execute_script("window.scrollBy(0, 10000)")

    def web_scroll_to_ele(self, types: str, locate: str, index: int = None) -> None:
        """
        scroll to the position of ele
        :param types: locate type
        :param locate: locator
        :param index: tag index
        :return:
        """
        el = None
        if index is not None:
            el = 's'
        target = self.driver_element(types, locate, el=el)
        logger.debug('scroll page')
        if index is not None:
            self.driver.execute_script("arguments[0].scrollIntoView();", target[index])
        else:
            self.driver.execute_script("arguments[0].scrollIntoView();", target)

    @property
    def web_current_window(self):

        """
        get the current window handle, can not use alone
        :return:
        """
        current_window = self.driver.current_window_handle
        logger.debug(f'get current window handle {current_window}')
        return current_window

    @property
    def web_all_handle(self):
        """
        get  all handles
        :return:  list
        """
        handle = self.driver.window_handles
        logger.debug(f'get all handle {handle}')
        return handle

    def web_switch_windows(self, index: int) -> EM or None:
        """
        switch the window
        :param index: the index of target handle
        :return:
        """
        handle = self.web_all_handle[index]

        try:
            logger.debug(f'switch to handle: {handle}')
            return self.driver.switch_to.window(handle)
        except Exception as e:
            logger.debug("error of switching to handle -> {0}".format(e))

    def web_switch_frame(self, types: str, locate: str, index: int = None) -> None:
        """
        switch frame
        :param types: locate type
        :param locate: locator
        :param index: index of the position
        :return:
        """
        el = None  # single/multiple  default find_element=None single  / if find_element = 's' multiple

        if index is not None:
            el = 'l'
        logger.debug('switch to iframe')
        if el is not None and index is not None:
            # locate with multiple locate, make use of index of list to click
            element = self.driver_element(types=types, locate=locate, el=el)[index]
            self.driver.switch_to.frame(element)
        else:
            # 单个定位点击
            element = self.driver_element(types=types, locate=locate)
            self.driver.switch_to.frame(element)

    def web_switch_default_content(self) -> None:
        """
        return default node
        :return:
        """
        logger.debug('return default node')
        self.driver.switch_to.default_content()

    def web_switch_parent_frame(self) -> None:
        """
        return parent node
        :return:
        """
        logger.debug('return parent node')
        self.driver.switch_to.parent_frame()

    def web_switch_to_alert(self) -> EM or None:
        """
        focus on alert
        """
        try:
            accept = self.driver.switch_to.alert
            logger.debug('focus on alert')
            return accept
        except Exception as e:
            logger.error("error when finding alert window-> {0}".format(e))

    def web_accept(self) -> EM or None:
        """
        click the accept when getting an alert
        :return:
        """
        try:
            accept = self.driver.switch_to.alert.accept()
            logger.debug('alert is accepted')
            return accept
        except Exception as e:
            logger.error("error when accepting alert-> {0}".format(e))

    def web_dismiss(self) -> EM or None:
        """
        click the cancel when getting an alert
        :return:
        """
        try:
            accept = self.driver.switch_to.alert.dismiss()
            logger.debug('alert is canceled')
            return accept
        except Exception as e:
            logger.error("error when dismissing alert-> {0}".format(e))

    def web_alert_text(self) -> None or str:
        """
        get the text from the alert window
        :return:
        """
        try:
            accept = self.driver.switch_to.alert.text
            logger.debug(f'get the content from alart: {accept}')
            return accept
        except Exception as e:
            logger.error("error when getting context from alert-> {0}".format(e))

    def screen_shot(self, doc: str, img_report: bool = True) -> str or None:
        """
        capture the current interface picture
        :param doc:  str name of picture
        :param img_report:  bool add img to testing report,default True
        :return:
        """

        filename = doc + "_" + str(round(time.time() * 1000)) + ".png"
        if len(filename) >= 200:
            filename = str(round(time.time() * 1000)) + ".png"
        filepath = os.path.join(RESULT_SCREEN_DIR, filename)

        self.driver.save_screenshot(filepath)
        if img_report:
            allure.attach(self.driver.get_screenshot_as_png(),
                          name=filename,
                          attachment_type=allure.attachment_type.PNG)
        logger.debug(f"save the screen in : {filepath}")
        return filepath

    def web_get_dropdown_options_count(self, types: str, locate: str) -> str or None:
        """
        get the count of dropdown options
        :param types: locate type
        :param locate: locator
        :return:
        """

        element = self.driver_element(types, locate)
        sel = Select(element)
        options = sel.options
        logger.debug(f'count of dropdown options : {options}')
        return options

    def web_element_hover(self, types: str, locate: str) -> EM or None:
        """
        hover to target position
        :param types: locate type
        :param locate: locator
        :return:
        """
        element = self.driver_element(types, locate)
        hover = ActionChains(self.driver).move_to_element(element).perform()
        logger.debug(f"position of mouse {locate}")
        return hover

    def web_element_hover_clicks(self, types: str, locate: str, index: int = None) -> None:
        """
        hover to target position and click
        :param types: locate type
        :param locate: locator
        :param index: index of list
        :return:
        """
        element = self.driver_element(types, locate)
        ActionChains(self.driver).move_to_element(element).perform()
        self.sleep(0.5)
        self.often_click(types=types, locate=locate, index=index)
        logger.debug(f"mouse hover at: {locate} click")

    def web_save_as_img(self, types: str, locate: str, filename: str, sleep: int = 1) -> None or str:
        """
        save img
        :param types: locate type
        :param locate: locator
        :param filename: name of img
        :param sleep: wait time, default 1s
        :return: str img path
        """
        if sys.platform.lower() == 'win32':
            import pyautogui, pyperclip
            # right click
            self.web_right_click(types=types, locate=locate)

            # save img as
            pyautogui.typewrite(['V'])

            # copy file and address
            pic_dir = None
            pyperclip.copy(os.path.join(RESULT_SCREEN_DIR, f'{filename}.jpg'))
            # wait for the save window, generally 0.8s
            self.sleep(sleep)
            # paste
            pyautogui.hotkey('ctrlleft', 'V')
            # save
            pyautogui.press('enter')
            logger.debug(f'path of pic: {filename}！')
            return pic_dir

    def web_select_locate(self, types: str, locate: str, value: str) -> None:
        """
        operate select， only  used with select tag
        :param types:  locate type
        :param locate: locator
        :param value:   #option content
            # select by index
            .select_by_index(1)
            # select by value
            .select_by_value("2")
            select_by_visible_text("Male")
            # select by option text
        :return:
        """
        selcet = self.driver_element(types, locate)
        Select(selcet).select_by_visible_text(value)
        logger.debug('web dropdown select')

    def web_is_element_displayed(self, types: str, locate: str) -> EM or None:
        """
        check if the element exists
        :param types:locate type
        :param locate: locator
        :return:
        """
        if types and locate is not None:
            element = self.driver_element(types, locate)
            displayed = element.is_displayed()
            return displayed
        else:
            logger.error('locate can not be empty')

    def web_title_contains(self, text: str) -> bool:
        """
        check if the current title contains str
        :param text:
        :return: bool
        """
        return EC.title_contains(text)(self.driver)

    def web_title_is(self, text: str) -> bool:
        """
        check if the current title is str
        :param text: content
        :return: bool
        """
        return EC.title_is(text)(self.driver)

    def web_presence_of_element_located(self, types: str, locate: str, ) -> bool:
        """
        check if the element is located
        检查是否加载到dom树
        :param types: locate type
        :param locate: locator
        :return: driver
        """
        types = self.get_by_type(types)

        wait = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                             poll_frequency=POLL_FREQUENCY)
        try:
            em = wait.until(EC.presence_of_element_located((types, locate)))
            if em:
                return True
            else:
                return False

        except Exception as e:
            logger.error(e)
            return False

    def web_visibility_of_element_located(self, types: str, locate: str, ) -> bool:
        """
        check if the element is visible
        :param types: locate type
        :param locate: locator
        :return: driver
        """
        types = self.get_by_type(types)

        wait = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                             poll_frequency=POLL_FREQUENCY)
        try:
            em = wait.until(EC.visibility_of_element_located((types, locate)))
            if em:
                return True
            else:
                return False

        except Exception as e:
            logger.error(e)
            return False

    def web_element_to_be_clickable(self, types: str, locate: str, ) -> bool or EM:
        """
        check if the element is clickable
        :param types: locate type
        :param locate: locator
        :return: driver
        """
        types = self.get_by_type(types)

        wait = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                             poll_frequency=POLL_FREQUENCY)
        try:
            em = wait.until(EC.element_to_be_clickable((types, locate)))
            if em:
                return em
        except Exception as e:
            logger.error(e)
            return False

    def web_frame_to_be_available_and_switch_to_it(self, types: str, locate: str, ) -> bool:
        """
        check if the element is available and switch to it
        :param types: locate type
        :param locate: locator
        :return: driver
        """
        types = self.get_by_type(types)

        wait = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                             poll_frequency=POLL_FREQUENCY)
        try:
            em = wait.until(EC.frame_to_be_available_and_switch_to_it((types, locate)))
            return em
        except Exception as e:
            logger.error(e)
            return False

    def web_element_to_be_selected(self, types: str, locate: str, ) -> bool:
        """
        check if the element is selected
        :param types: locate type
        :param locate: locator
        :return: driver
        """
        types = self.get_by_type(types)

        wait = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                             poll_frequency=POLL_FREQUENCY)
        try:
            em = wait.until(EC.element_to_be_selected((types, locate)))
            return em
        except Exception as e:
            logger.error(e)
            return False

    def web_send_enter_key(self, types: str, locate: str, index: int = None) -> None:
        """
        send enter key
        :param types:
        :param locate:
        :param index:
        :return:
        """
        el = None
        if index is not None:
            el = 'l'
        logger.debug('click enter')
        if el is not None and index is not None:
            # multiple
            self.driver_element(types=types, locate=locate, el=el)[index].send_keys(Keys.ENTER)
        else:
            # return first one
            self.driver_element(types=types, locate=locate).send_keys(Keys.ENTER)

    def web_send_down_or_up_key(self, types: str, locate: str, index: int = None, key: str = 'down') -> None:
        """
        press up or down
        :param types:
        :param locate:
        :param index:
        :param key: down or up
        :return:
        """
        el = None
        logger.debug('click up')
        if index is not None:
            el = 'l'

        if key == 'down':
            keys = Keys.DOWN
        else:
            keys = Keys.UP

        if el is not None and index is not None:
            self.driver_element(types=types, locate=locate, el=el)[index].send_keys(keys)
        else:
            self.driver_element(types=types, locate=locate).send_keys(keys)

    def driver_element(self, types: str, locate: str, el: str = None, ) -> EM or None:
        """
        return element
        :param types: locate type
        :param locate: locator
        :param el:
        :return: driver
        """
        types = self.get_by_type(types)

        if el is not None:  # find_elements
            element = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                                    poll_frequency=POLL_FREQUENCY).until(
                lambda x: x.find_elements(types, locate))
            return element
        else:  # find_element
            element = WebDriverWait(self.driver, timeout=IMPLICITLY_WAIT_TIME,
                                    poll_frequency=POLL_FREQUENCY).until(
                lambda x: x.find_element(types, locate))
            return element

    def web_submit(self, types: str, locate: str, index: int = None) -> None:
        """
        submit form
        :param types: locate type
        :param locate: locator
        :param index: index of list
        :return:
        """
        el = None
        if index is not None:
            el = 'l'
        logger.debug('submit form')
        if el is not None and index is not None:
            #
            self.driver_element(types=types, locate=locate, el=el)[index].submit()
        else:
            #
            self.driver_element(types=types, locate=locate).submit()

    def web_right_click(self, types: str, locate: str, index: int = None) -> None:
        """
        right click
        :param types: locate type
        :param locate: locator
        :param index: index of list,  find_element
        :return:
        """
        el = None
        if index is not None:
            el = 'l'
        logger.debug('right click')
        if el is not None and index is not None:
            element = self.driver_element(types=types, locate=locate, el=el)[index].click()
            ActionChains(self.driver).context_click(element).perform()
        else:
            # single locate click
            element = self.driver_element(types=types, locate=locate, ).click()
            ActionChains(self.driver).context_click(element).perform()

    def web_double_click(self, types: str, locate: str, index: int = None) -> None:
        """
        double click
        :param types: locate type
        :param locate: locator
        :param index: index of list,  find_element
        :return:
        """
        el = None  #
        if index is not None:
            el = 'l'
        logger.debug('double click')
        if el is not None and index is not None:
            element = self.driver_element(types=types, locate=locate, el=el)[index]
            ActionChains(self.driver).double_click(element).perform()
        else:

            element = self.driver_element(types=types, locate=locate)
            ActionChains(self.driver).double_click(element).perform()

    def web_js_clear(self, types: str, locate: str, index: int = None) -> None:
        """
        clear input with js
        :param types: locate type
        :param locate: locator
        :param index: index of list,  find_element
        :return:
        """
        el = None  # single/multiple  default find_element=None  / if find_element = 's' then multiple
        if index is not None:
            el = 'l'
        logger.debug('web clear input with js')
        if el is not None and index is not None:
            element = self.driver_element(types=types, locate=locate, el=el)[index]
        else:
            element = self.driver_element(types=types, locate=locate)

        self.driver.execute_script("arguments[0].value = '';", element)

    def web_execute_js(self, js: str) -> None:
        """
        execute js
        :param js: js str
        """
        logger.debug('web execute js')
        self.driver.execute_script(js)

    def web_jsclear_continue_input(self, types: str, locate: str, text: str, index: int = None) -> None:
        """
        clear and input
        :param types: locate type
        :param locate: locator
        :param text: input text
        :param index: index of list
        :return:
        """
        logger.debug('clear by js and then input')
        self.web_js_clear(types=types, locate=locate, index=index)
        self.sleep(0.5)
        self.often_input(types=types, locate=locate, text=text, index=index)

    def often_text(self, types: str, locate: str, index: int = None) -> None or EM:
        """
        get content of text tag
        :param types: locate type
        :param locate: locator
        :param el:
        :return: driver
        """
        el = None  # single/multiple  default find_element=None  / if find_element = 's' then multiple
        if index is not None:
            el = 'l'
        logger.debug('get content of text tag')
        if el is not None and index is not None:
            #
            return self.driver_element(types=types, locate=locate, el=el)[index].text
        else:
            #
            return self.driver_element(types=types, locate=locate).text

    def often_click(self, types: str, locate: str, index: int = None) -> None:
        """
        get element and then click
        :param types: locate type
        :param locate: locator
        :param index: index of element list
        :return:
        """
        el = None  # single/multiple  default find_element=None  / if find_element = 's' then multiple
        if index is not None:
            el = 'l'
        logger.debug('find  and click')
        if el is not None and index is not None:
            #
            self.driver_element(types=types, locate=locate, el=el)[index].click()
        else:
            #
            self.driver_element(types=types, locate=locate).click()

    def often_input(self, types: str, locate: str, text: str, index: int = None) -> None:
        """
        get element and type in (also support the input keys)
        :param types: locate type
        :param locate:  locator
        :param text:  index
        :param index: index
        :return:
        """
        el = None  # single/multiple  default find_element=None  / if find_element = 's' then multiple
        if index is not None:
            el = 'l'
        logger.debug('type in some content')
        if el is not None and index is not None:
            self.driver_element(types=types, locate=locate, el=el)[index].send_keys(text)
        else:
            self.driver_element(types=types, locate=locate, ).send_keys(text)

    def often_clear(self, types: str, locate: str, index: int = None) -> None:
        """
        clear input, if it does not work then try to use js_clear
        :param types: locate type
        :param locate: locator
        :param index: index
        """
        el = None  # single/multiple  default find_element=None  / if find_element = 's' then multiple
        if index is not None:
            el = 'l'
        logger.debug('clear')
        if el is not None and index is not None:
            self.driver_element(types=types, locate=locate, el=el)[index].clear()
        else:
            self.driver_element(types=types, locate=locate).clear()

    def often_clear_continue_input(self, types: str, locate: str, text: str, index: int = None) -> None:
        """
        clear and then input
        :param types:
        :param locate:
        :param text:
        :param index:
        :return:
        """
        logger.debug('clear input and then input')
        self.often_clear(types=types, locate=locate, index=index)
        self.sleep(0.5)
        self.often_input(types=types, locate=locate, text=text, index=index)

    def get_case(self, yaml_names=None, case_names=None):
        """
        get case date
        :param yaml_names: yaml path
        :param case_names:  case name
        :return:
        """
        if yaml_names is not None:
            d = GetCaseYaml(yaml_name=yaml_names, case_name=case_names)
            return d
        else:
            raise ErrorException('path of yaml can not be empty！')


class Web(Base):
    """
     common locate types:  id,xpath,link_text/link,partial_link_text/partial,name,
        tag_name/tag,class_name/class,css_selector/css
    """

    def web_judge_execution(self, types, locate, operate=None, text=None, notes=None, index=None, wait=None):
        """
          operation types:
        operate type                                action
        input                       >               type in
        click                       >               click the element
        text                        >               text
        submit                      >               submit form
        scroll                      >               scroll and slide down
        clear                       >               clear the content of input
        jsclear                     >               js clear
        jsclear_continue_input      >               clear js and then input
        clear_continue_input        >               clear and then input
        web_url                     >               get the current url
        web_title                   >               get the current title
        web_html_content            >               the html content
        iframe                      >               change the frame
        :param locate:
        :param operate:
        :param text:
        :param index:
        :param wait:
        :return:

        """

        if operate not in Operation.web_operation.value:
            logger.error(f'the operation {operate} is not supported yet！！！')
            logger.error(f'only support {Operation.web_operation.value} right now')
            raise ErrorException(f'the operation {operate} is not supported yet！！！')

        if operate is None:
            el = index  # default multiple if index is empty
            return self.driver_element(types=types, locate=locate, el=el)

        else:
            if operate == 'input':  # input
                if text is not None:
                    self.sleep(wait)
                    logger.debug(notes)
                    return self.often_input(types=types, locate=locate, text=text, index=index)
                else:
                    logger.error(' the text param is needed for a function')

            elif operate == 'click':  # click
                self.sleep(wait)
                logger.debug(notes)
                return self.often_click(types=types, locate=locate, index=index)

            elif operate == 'text':  # extract text
                self.sleep(wait)
                logger.debug(notes)
                return self.often_text(types=types, locate=locate, index=index)

            elif operate == 'submit':  # submit
                self.sleep(wait)
                logger.debug(notes)
                return self.web_submit(types=types, locate=locate, index=index)

            elif operate == 'scroll':  # scroll
                self.sleep(wait)
                logger.debug(notes)
                return self.web_scroll_to_ele(types=types, locate=locate, index=index)

            elif operate == 'clear':  # clear
                self.sleep(wait)
                logger.debug(notes)
                return self.often_clear(types=types, locate=locate, index=index)

            elif operate == 'jsclear':  # clear with js
                self.sleep(wait)
                logger.debug(notes)
                return self.web_js_clear(types=types, locate=locate, index=index)

            elif operate == 'jsclear_continue_input':  # clear by js and then input
                if text is not None:
                    self.sleep(wait)
                    logger.debug(notes)
                    return self.web_jsclear_continue_input(types=types, locate=locate, text=text, index=index)
                else:
                    logger.error(' the text param is needed for a function')

            elif operate == 'clear_continue_input':  # clear and then input
                if text is not None:
                    self.sleep(wait)
                    return self.often_clear_continue_input(types=types, locate=locate, text=text, index=index)
                else:
                    logger.debug(' the text param is needed for a function')

            elif operate == 'iframe':  # iframe change   switch_default_content (outermost layer) switch_parent_frame
                self.sleep(wait)
                logger.debug(notes)
                return self.web_switch_frame(types=types, locate=locate, index=index)

            elif operate == 'web_url':  # get current url
                self.sleep(wait)
                logger.debug(notes)
                return self.web_url

            elif operate == 'web_title':  # title
                self.sleep(wait)
                logger.debug(notes)
                return self.web_title

            elif operate == 'web_html_content':  # htmle content
                self.sleep(wait)
                logger.debug(notes)
                return self.web_html_content

    def webexe(self, yaml_file, case, text=None, wait=0.1):
        """
        execute steps
        :param yaml_file:  yaml
        :param case: yaml cases
        :param text:  context
        :param wait:  wait time: s
        :return:
        """
        result = None  # result of assert

        yaml = replace_py_yaml(yaml_file)

        locator_data = self.get_case(yaml, case)
        locator_step = locator_data.step_count()

        for locator in range(locator_step):
            if locator_data.operate(locator) in ('input', 'clear_continue_input', 'jsclear_continue_input'):
                self.web_judge_execution(types=locator_data.types(locator), locate=locator_data.locate(locator),
                                         operate=locator_data.operate(locator), notes=locator_data.info(locator),
                                         text=text, index=locator_data.list_index(locator))
            else:
                result = self.web_judge_execution(types=locator_data.types(locator),
                                                  locate=locator_data.locate(locator),
                                                  operate=locator_data.operate(locator),
                                                  notes=locator_data.info(locator),
                                                  index=locator_data.list_index(locator))
            self.sleep(wait)
        return result


class AutoRunCase(Web):
    """
    run test cases automatically
    """

    def run(self, yaml_file, case, test_data=None, forwait=None):
        """
        execute locating steps, test_data is an iterative object when using run function
        :param yaml_file:  yaml
        :param case: yaml case
        :param test_data:  test data
        :param forwait:  wait time /s
        :return:
        """

        result = None

        yaml = replace_py_yaml(yaml_file)

        locator_data = self.get_case(yaml, case)
        test_dict = locator_data.test_data()

        locator_step = locator_data.step_count()

        for locator in range(locator_step):

            if locator_data.operate(locator) in ('input', 'clear_continue_input', 'jsclear_continue_input'):

                self.web_judge_execution(types=locator_data.types(locator), locate=locator_data.locate(locator),
                                         operate=locator_data.operate(locator), notes=locator_data.info(locator),
                                         text=test_data[locator], index=locator_data.list_index(locator),
                                         wait=locator_data.local_wait(locator))
            else:
                result = self.web_judge_execution(types=locator_data.types(locator),
                                                  locate=locator_data.locate(locator),
                                                  operate=locator_data.operate(locator),
                                                  notes=locator_data.info(locator),
                                                  index=locator_data.list_index(locator),
                                                  wait=locator_data.local_wait(locator))
            self.sleep(forwait)

        # assert
        if ('assertion' and 'assertype') in test_dict[0] and result:  # only available when the assertion is needed
            is_assertion(test_data, result)
        # return relust
