# Author : Michael Yang
# Date   : 9:43 am - 7/10/22
# File   : google.py

import os
import sys

sys.path.append(os.pardir)
from common import Web


class Google(Web):
    """
    page object of google
    """

    def input_search_content(self, content):
        """
        type in searching content
        :param content:
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name, text=content)

    def click_search_button(self):
        """
        click the search button
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)
