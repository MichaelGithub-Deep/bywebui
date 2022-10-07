# Author : Michael Yang
# Date   : 5:21 pm - 5/10/22
# File   : common.py
import os
import re
import shutil
import sys
import time
from typing import TypeVar, Tuple

import cv2
import numpy as np
import yaml
from loguru import logger

from config import RESULT_ALLURE_DIR, RESULT_JSON_DIR, RESULT_SCREEN_DIR, LOG_DIR, DIFF_IMGPATH, SETTING_YAML_DIR

T = TypeVar('T')


def read_conf(value: str) -> list or dict or str:
    """
    read configuration file with yaml
    :param value: read key
    :return:
    """
    try:
        with open(SETTING_YAML_DIR, encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            for item in data:
                if item.get(value) is not None:
                    return item.get(value)
    except Exception as e:
        logger.error(f'read setting yaml exception: {e}')


def find_dict(target_dist: dict, find_keys: T) -> list or int:
    """
    find the value list based on the keys
    :param target_dist: target dict
    :param find_keys: the keys
    :return:
    """
    value_found = []
    if isinstance(target_dist, list):  # deal with list situation
        if len(target_dist) > 0:
            for item in target_dist:
                found = find_dict(item, find_keys)
                if found:
                    value_found.extend(found)
            return value_found
    if not isinstance(target_dist, dict):  # no more dict type data
        return 0
    else:  # search for the target dict from next layer
        dict_key = target_dist.keys()
        for i in dict_key:
            if i == find_keys:
                value_found.append(target_dist[i])
            found = find_dict(target_dist[i], find_keys)
            if found:
                value_found.extend(found)
        return value_found


def is_assertion(dicts: T, actual: T) -> None:
    """
    assert
    :param dicts:  dict assert params
    :param actual: actual result
    :return:
    """

    if dicts is not None:
        is_assertion_results(actual=actual, expect=dicts[-2], types=dicts[-1])


def is_assertion_results(actual: T, expect: T, types: str) -> bool:
    """
    assert function
    :param actual: actual result
    :param expect: expected result
    :param types:  assert type  ==(equal) !=(not equal) in(contains) notin(not contain)
    :return:
    """
    if isinstance(actual, dict):
        if isinstance(expect, dict):
            actual = find_dict(actual, list(expect)[0])  # 利用字典的键获取断言的值
            expect = list(expect.values())[0]
    if types == '==':
        assert expect == actual
        return True

    elif types == '!=':
        assert expect != actual
        return True

    elif types == 'in':
        assert expect in actual
        return True

    elif types == 'notin':
        assert expect not in actual
        return True

    elif types is None:
        return False
    else:
        logger.error(f'the input type: {types} does not support yet！！')
        return False


class ErrorException(Exception):
    """
    self defined exception class
    """

    def __init__(self, message):
        super.__init__(message)


levels = read_conf('CURRENCY').get('LEVEL')


class SetLog:
    """
    log setting class,  based on loguru
    """
    DAY = time.strftime("%Y-%m-%d", time.localtime(time.time()))  # YYYY-mm-dd

    # set the path of log
    LOG_PATH = os.path.join(LOG_DIR, f'{DAY}_all.log')
    ERR_LOG_PATH = os.path.join(LOG_DIR, f'{DAY}_err.log')

    logger.add(LOG_PATH, rotation="00:00", encoding='utf-8')
    logger.add(ERR_LOG_PATH, rotation="00:00", encoding='utf-8', level='ERROR', )
    logger.remove()  # delete the handler made automatically after importing logger,
    # there would be repeated output if it is not deleted

    handler_id = logger.add(sys.stderr, level=levels)  # add a handler which can be updated and controlled


class DeleteReport:
    """
    delete the report
    """

    def make_dir(self, path: str) -> None:
        """
        make dir if it does not exist
        :param path:
        :return:
        """
        folder = os.path.exists(path)
        if not folder:  # make one if it does not exist
            os.makedirs(path)
        else:
            pass

    def clear_report(self, file_path: str) -> None:
        """
        clear the testing report
        :param file_path: report path
        :return:
        """
        del_list = os.listdir(file_path)
        if del_list:
            try:
                for f in del_list:
                    file = os.path.join(file_path, f)

                    # see if it is a file
                    if os.path.isfile(file):
                        if not file.endswith('.xml'):  # do not delete .xml file
                            os.remove(file)
                    else:
                        if os.path.isdir(file):
                            shutil.rmtree(file)
            except Exception as e:
                logger.error(e)

    def run_del_report(self, ) -> None:
        """
        delete the reports
        :return:
        """
        is_clean_report = read_conf('CURRENCY').get('IS_CLEAN_REPORT')
        if is_clean_report:  # clear the reports in RESULT_ALLURE_DIR,RESULT_JSON_DIR,RESULT_SCREEN_DIR if it's True

            try:
                dir_list = [RESULT_ALLURE_DIR, RESULT_JSON_DIR, RESULT_SCREEN_DIR]
                for item in dir_list:
                    self.make_dir(item)
                    self.clear_report(item)
                logger.info('clearing the reports.....')
            except Exception as e:
                logger.error(e)

        else:
            logger.warning('clear report is disabled！！')