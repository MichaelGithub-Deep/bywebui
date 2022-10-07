# Author : Michael Yang
# Date   : 10:02 am - 7/10/22
# File   : test_google.py
import allure
import pytest
from page_object.google import Google
from common.read_data import read_pytest_data


class TestGoogle:

    @allure.feature("google search")  # feature of testcase
    @allure.story("searching check")  # module
    @allure.title("type in data and search")  # title of testcase
    @allure.description('type in multiple params')  # description of testcase
    @pytest.mark.testgoogle_web  # case tag
    @pytest.mark.parametrize('content', read_pytest_data(__file__, 'test_google_search'))  # test data
    def test_baidu_search(self, GetDriver, content):
        google = Google(GetDriver)

        with allure.step('type in content'):
            google.input_search_content(content)

        with allure.step('click search'):
            google.click_search_button()

            google.sleep(3)

            # 对比查询后图片结果
            search_relust = google.screen_shot('search')
