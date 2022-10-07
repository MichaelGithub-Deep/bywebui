# Author : Michael Yang
# Date   : 9:26 pm - 5/10/22
# File   : read_data.py

import os
import pickle
from typing import List, Tuple

import yaml
from faker import Factory
from xlrd import open_workbook

from config import CASE_YMAL_DIR, LOCATOR_YMAL_DIR
from common.common import ErrorException, logger, read_conf

fake = Factory().create('zh_CN')


# read data from excel
class RedaExcel:
    """
    *xrld ==1.2.0
    read data from excel and return list
    demo：
    content in excel：
    | A  | B  | C  | x |
    | A1 | B1 | C1 | . |
    | A2 | B2 | C2 | . |

    return list：
    [{A: A1, B: B1, C:C1}, {A:A2, B:B2, C:C2}]

    return list if line=False ：
    [[A,B,C], [A1,B1,C1], [A2,B2,C2]]

    get data from an appointed sheet by the index or name of sheet:
    ExcelReader(excel, sheet=2)
    ExcelReader(excel, sheet='Test')
    """

    def __init__(self, excel: str, sheet: int or str = 0, line: bool = True):
        if os.path.exists(excel):
            self.excel = excel
        else:
            raise FileNotFoundError(f'The excel: {excel} does not exist !!!')
        self.sheet = sheet
        self.title_line = line
        self._data = list()

    @property
    def data(self):
        if not self._data:
            workbook = open_workbook(self.excel)

            if type(self.sheet) not in [int, str]:
                raise ErrorException('Sheet Type Error!!!')
            elif type(self.sheet) == int:
                s = workbook.sheet_by_index(self.sheet)
            else:
                s = workbook.sheet_by_name(self.sheet)

            if self.title_line:
                title = s.row_values(0)  # first line is the title
                for col in range(1, s.nrows):  # traverse the remaining rows in turn, forming a dict with the first row
                    self._data.append(dict(zip(title, s.row_values(col))))
            else:
                for col in range(0, s.nrows):  # return all rows with every row as a list
                    self._data.append(s.row_values(col))
        return self._data


# read data from yaml
class GetCaseYaml:
    """
    locator data: locatorYaml
    """

    def __init__(self, yaml_name: str, case_name: str = None) -> None:
        """
        init method
        :param yaml_name: name of yaml file
        :param case_name: case name
        """

        self.yaml_name = yaml_name  # name of yaml file (contacted path)

        if case_name is not None:  # it automatically identifies whether to read location data or test data
            # if the case name is not empty
            self.model_name = yaml_name  # module name: name of yaml file
            self.case_name = case_name  # testcase name: name of testcase

            if case_name.startswith('test'):
                self.FLIE_PATH = os.path.join(CASE_YMAL_DIR, f"{self.yaml_name}")
            else:
                self.FLIE_PATH = os.path.join(LOCATOR_YMAL_DIR, f"{self.yaml_name}")
        else:  # return the locator path directly when there is no testcase name
            self.FLIE_PATH = os.path.join(LOCATOR_YMAL_DIR, f"{self.yaml_name}")

    def open_yaml(self):
        """
        read yaml
        :return: dict
        """
        try:
            with open(self.FLIE_PATH, encoding='utf-8') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                f.close()
                return data
        except UnicodeDecodeError:
            with open(self.FLIE_PATH, encoding='GBK') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                f.close()
                return data
        except Exception as e:
            logger.error(f'Error opening yaml file.error: {e}')

    def get_yaml(self):
        """
        return data of yaml file
        :return: dict
        """
        yaml_data = self.open_yaml()
        if yaml_data is not None:
            return yaml_data[1:]  # remove the module
        else:
            logger.error('The yaml file is empty')
            raise 'The yaml file is empty'

    def get_current_data(self):
        """
        return all data of the current column
        :return: dict
        """
        yaml_list = self.get_yaml()
        for yaml in yaml_list:
            # return the current data if case name equals self.case_name
            if yaml.get('case_name') == self.case_name:
                return yaml
        return "case name does not exist!!！"

    def count_test_data(self):
        """
        count the sum of yaml test data
        :return:
        """
        yaml_list = self.get_yaml()
        for yaml in yaml_list:
            # return the current data if case name equals self.case_name
            if yaml.get('case_name') == self.case_name:
                try:
                    testdata_len = len(yaml.get('testdata'))

                    return testdata_len
                except Exception as e:
                    logger.error(e)

    def data_count(self):
        """
        count the sum of yaml test data
        :return:
        """
        return self.count_test_data()

    def step_count(self):
        """
        count of testing step
        :return:
        """
        data_ist = self.get_yaml()

        if data_ist:
            for data in data_ist:
                # return the current data if case name equals self.case_name
                if data.get('case_name') == self.case_name:
                    return len(data.get('element'))
        else:
            logger.error('test case does not exist, please check the yaml file')
            raise ErrorException('test case does not exist, please check the yaml file')

    def get_param(self, value: str) -> str:
        """
        get the case params
        :param value:
        :return:
        """

        yaml_list = self.get_yaml()
        for yaml in yaml_list:
            # return the current data if case name equals self.case_name
            if yaml.get('case_name') == self.case_name:
                return yaml.get(value)
        return "case_name does not exist！"

    def get_set(self, index: int, vaule: str):
        """
        get the set step data
        :param index: index
        :param vaule:  value
        :return:
        """
        data_list = self.get_yaml()
        if index < self.step_count():
            for data in data_list:
                #
                if data.get('case_name') == self.case_name:
                    return data.get('element')[index].get(vaule)
        logger.error(f'there is only {self.step_count()} steps in {self.case_name}，but you typed in {index} steps！')
        return None

    @property
    def get_model(self):
        """
        get model data
        :return: dict
        """
        data = self.open_yaml()
        return data[0].get('model')  #

    @property
    def title(self):
        """
        get title of test case
        :return: str
        """
        return self.get_param('title')

    @property
    def precondition(self):
        """
        return all precondition
        :return: str
        """
        return self.get_param('precondition')

    @property
    def request_type(self):
        """
        ** HTTP request type
        :return: str
        """
        return self.get_param('request_type')

    @property
    def header(self):
        """
        ** HTTP reqeust header
        :return: str
        """
        return self.get_param('header')

    @property
    def urlpath(self):
        """
        ** HTTP url path
        :return: str
        """
        return self.get_param('urlpath')

    def test_data_values(self, ):
        """
        get values of test data from yaml
        :return:  demo [('u1', 'p1', 'i1'), ('u2', 'p2', 'i2'), ('u3', 'p3', 'i3')]
        """

        data_values_list = []

        data_lists = self.get_yaml()

        for data in data_lists:

            if data.get('case_name') == self.case_name:
                data_list = data.get('testdata')
                if data_list is not None:
                    for i in data_list:
                        data_values_list.append(tuple(i.values()))
                    return data_values_list
                else:
                    logger.info(f'there is no test data in current data: {data}')
                    continue

    def test_data_list(self, index: int, agrs: str) -> str:
        """
        return test case data
        :param index: index
        :param agrs: key
        :return:
        """
        data_lists = self.get_yaml()

        if index < self.dataCount():

            for data in data_lists:
                if data.get('case_name') == self.case_name:
                    return data.get('testdata')[index].get(agrs)

        logger.error(f'there is only {self.step_count()} steps in {self.case_name}，but you typed in {index} steps！')

    def test_data(self):
        """
        return all test data
        :return:
        """
        return self.get_current_data().get('testdata')

    def casesteid(self, index: int) -> int:
        """
        return casesetid params
        """
        return self.get_set(index, 'casesetid')

    def types(self, index: int) -> str:
        """
        return types params
        """
        return self.get_set(index, 'types')

    def operate(self, index: int) -> str:
        """
        return operate params
        """
        return self.get_set(index, 'operate')

    def locate(self, index: int) -> str:
        """
        return locate params
        """
        return self.get_set(index, 'locate')

    def list_index(self, index: int) -> int:
        """
        return list index params
        """
        return self.get_set(index, 'list_index')

    def local_wait(self, index: int or float) -> int or float:
        """
        return local wait params
        """
        return self.get_set(index, 'local_wait')

    def info(self, index: int) -> str:
        """
        return info params
        """
        return self.get_set(index, 'info')


# faker random data
class RandomData:
    """
    based on fake
    """

    @property
    def random_name(self):
        """
        name
        :return: str
        """
        return fake.name()

    @property
    def random_phone_number(self):
        """
        phone number
        :return:  int
        """
        return fake.phone_number()

    @property
    def random_email(self):
        """
        email
        :return:
        """
        return fake.email()

    @property
    def random_job(self):
        """
       job name
       :return:
       """
        return fake.job()

    @property
    def random_ssn(self):
        """
       state name
       :return:
       """
        return fake.ssn(min_age=18, max_age=90)

    @property
    def random_company(self):
        """
        company name
        :return:
        """
        return fake.company()

    @property
    def random_city(self):
        """
        cite
        :return:  str
        """
        return fake.city_name()

    @property
    def random_province(self):
        """
        province name
        :return:  str
        """
        return fake.province()

    @property
    def random_country(self):
        """
        country name
        :return:  str
        """
        return fake.country()

    @property
    def random_address(self):
        """
        address name
        :return:  str
        """
        return fake.address()

    @property
    def random_time(self):
        """
        time 24H   22:00:00
        :return: str
        """
        return fake.time()

    @property
    def random_year(self):
        """
        year
        :return: str[0] - number month  str[1] - english  monthe
        """
        return (fake.month(), fake.month_name())

    @property
    def random_month(self):
        """
        month
        :return: str
        """
        return fake.month()

    @property
    def random_date_this_month(self):
        """
        local time of this month
        :return: str
        """
        return fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None)

    @property
    def random_date_this_decade(self):
        """
        local time of this year
        :return: str
        """
        return fake.date_time_this_year(before_now=True, after_now=False, tzinfo=None)

    @property
    def random_date_time_this_century(self):
        """
        local time of this centry
        :return: str
        """
        return fake.date_time_this_century(before_now=True, after_now=False, tzinfo=None)

    @property
    def random_day_of_week(self):
        """
        week
        :return:  str
        """
        return fake.day_of_week()

    def random_date_of_birth(self, age):
        """
        bithday
        :param age:  int  age range
        :return:  str
        """
        return fake.date_of_birth(tzinfo=None, minimum_age=0, maximum_age=age)


def replace_py_yaml(file):
    """
    change the py to yaml postfix
    :param file:
    :return:
    """
    return os.path.basename(file).replace('py', 'yaml')


# get test data (tuple) WEB
def read_pytest_data(yaml_name: str, case_name: str, ) -> List or Tuple:
    """
    * pytest.mark.parametrize()  * only used in pytest architecture
    *
    :param yaml_name: yaml name
    :param case_name:   testcase data
    :return:
    """
    yaml = replace_py_yaml(yaml_name)
    testdata = GetCaseYaml(yaml, case_name).test_data_values()
    return testdata


#  get testing data of http
def read_api_case_data(yaml_name: str, case_name: str) -> List or Tuple:
    """
    http testing data
    :return:
    """
    yaml = replace_py_yaml(yaml_name)
    testdata = GetCaseYaml(yaml, case_name)

    return testdata.test_data()


# test method
if __name__ == '__main__':
    # IS_CLEAN_REPORT=read_setting_yaml()[0].get('IS_CLEAN_REPORT')
    # print(read_setting_yaml()[0].get('CURRENCY').get('IS_CLEAN_REPORT'))
    # print(read_setting_yaml())

    print(read_conf('CURRENCY').get('IS_CLEAN_REPORT'))
