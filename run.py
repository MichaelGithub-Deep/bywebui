# Author : Michael Yang
# Date   : 5:15 pm - 5/10/22
# File   : run.py

import os
import sys

sys.path.append(os.pardir)

from typing import List

import pytest

from config import *
from common.common import DeleteReport, ErrorException, logger

OUT_TITLE = """
══════════════════════════════════════════
║            WEB-UI-AUTO                 ║
║       stay hungry stay foolish ! !     ║
══════════════════════════════════════════
"""

logger.info(OUT_TITLE)


class RunPytest:

    @classmethod
    def value_division(cls, mlist: List) -> str:
        """
        divide module  generate demo '{} or {} or {}  '.format(mlist[0], mlist[1], mlist[2]) based on the length {} or
        """
        if mlist is not None:
            mdata = ''
            for index, i in enumerate(mlist):
                mdata += str(i)
                if index < len(mlist) - 1:
                    mdata += ' or '
            return mdata

    @classmethod
    def run_module(cls, m, n, reruns, mlist, dir):
        """
        run module
        :param m:  module
        :param n: thread count
        :param reruns:  retun count if failed
        :param mlist:  module list
        :param dir: name of test report
        :return:
        """
        var = cls.value_division(mlist)
        JSON_DIR = dir
        if m == 'all':  # all run all test cases
            logger.info('run all test cases of this report！！！')
            pytest.main(
                [f'-n={n}', f'--reruns={reruns}', '--alluredir', f'{JSON_DIR}', f'{CASE_DIR}'])
            return True

        elif ',' not in m and m != 'all' and m.startswith('test'):  # only one module
            logger.info(f'start to run module: {m}！！！')
            pytest.main(['-m', f'{m}', f'-n={n}', f'--reruns={reruns}', '--alluredir', f'{JSON_DIR}', f'{CASE_DIR}'])
            return True

        elif ',' in m and len(mlist) <= 5:  # run multiple modules
            logger.info(f'start to run module: {mlist}！！！')
            pytest.main(
                ['-m', f'{var}', f'-n={n}', f'--reruns={reruns}', '--alluredir', f'{JSON_DIR}', f'{CASE_DIR}'])
            return True

        else:  # module error
            logger.error(f'module error！！！')
            return False

    @classmethod
    def output_path(cls, dir):
        """
        generate the path of test report
        :param dir: dir name
        :return:
        """
        # json dir
        report_json_dir = os.path.join(BASE_DIR, "result", "{}".format(dir), "report_json")

        # allure report dir
        report_allure_dir = os.path.join(BASE_DIR, "result", "{}".format(dir), "report_allure")

        # make dir if the generated path does not exist
        list_path_dir = [report_json_dir, report_allure_dir]
        for pathdir in list_path_dir:
            if not os.path.exists(pathdir):
                os.makedirs(pathdir)

        return report_json_dir, report_allure_dir

    @classmethod
    def receiving_argv(cls):
        """
        接收系统输入参数   1 module name 2 thread num
        3 rerun count if failed 4 result name eg:  Python run.py all 1 1 demo
        :return:
        """
        # 1 module name
        try:
            module_name = sys.argv[1]
            mlist = None
            if ',' in module_name:
                mlist = module_name.split(',')

            # 2 thread num
            thread_num = sys.argv[2]

            # 3 rerun count
            reruns = sys.argv[3]

            # 4 result name
            results_dir = sys.argv[4]

            if int(thread_num) <= 0 or int(thread_num) is None:
                thread_num = 1
            if int(reruns) <= 0 or int(reruns) is None:
                reruns = 1
            return results_dir, module_name, mlist, thread_num, reruns
        except Exception as e:
            logger.error(e)
            raise ErrorException('input params error！')

    @classmethod
    def notice_type(cls, types: str, content: str = 'notification！！'):
        """
        reserved
        :param types:
        :param content:
        :return:
        """
        pass

    @classmethod
    def run(cls):
        """
        run all scripts, reserved for platform
        :return:
        """

        # clear the history report
        DeleteReport().run_del_report()

        # receive params
        results_dir, module_name, mlist, thread_num, reruns = cls.receiving_argv()

        # the path of test report
        report_json_dir, report_allure_dir = cls.output_path(results_dir)

        # run module
        run_module = cls.run_modle(module_name, thread_num, reruns, mlist, report_json_dir)

        # generate test report
        if run_module:
            os.system(f'allure generate {report_json_dir} -o {report_allure_dir} --clean')
            logger.info('generated test resport！')

        html_index = os.path.join(report_allure_dir, 'index.html')
        logger.info(html_index)

        return html_index

    @staticmethod
    def run_debug():
        """
        debug
        :return:
        """

        # clear the history report
        DeleteReport().run_del_report()

        pytest.main(
            ['-m', 'testgoogle_web', '-n=1', '--reruns=0', '--alluredir', f'{RESULT_JSON_DIR}', f'{CASE_DIR}'])

        # generate test report
        print(f'allure generate {RESULT_JSON_DIR} -o {RESULT_ALLURE_DIR} --clean')
        os.system(f'allure generate {RESULT_JSON_DIR} -o {RESULT_ALLURE_DIR} --clean')
        logger.info('generated test report ！')


if __name__ == '__main__':
    # RunPytest.run()
    RunPytest.run_debug()
