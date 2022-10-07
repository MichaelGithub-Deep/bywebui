# Author : Michael Yang
# Date   : 5:07 pm - 5/10/22
# File   : __init__.py.py
import os


__all__ = ['BASE_DIR', 'LINUX_CHROMEDRIVER', 'LINUX_FIREFOXDRIVER', 'IE_PATH', 'WIN_CHROMEDRIVER',
           'WIN_FIREFOXDRIVER', 'MAC_CHROMEDRIVER', 'MAC_FIREFOXDRIVER', 'LOG_DIR', 'CASE_DIR',
           'CASE_YMAL_DIR', 'LOCATOR_YMAL_DIR', 'DATA_FILE', 'DIFF_IMGPATH', 'SETTING_YAML_DIR',
           'RESULT_JSON_DIR', 'RESULT_ALLURE_DIR', 'RESULT_SCREEN_DIR', 'RESULT_TEMP_DIR'
          ]

# project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# browser driver path of mac
MAC_CHROMEDRIVER = os.path.join(BASE_DIR, "driver", "mac", "chromedriver")                 # chrome browser
MAC_FIREFOXDRIVER = os.path.join(BASE_DIR, "driver", "mac", "geckodriver")                 # firefox browser

# browser driver path of linux
LINUX_CHROMEDRIVER = os.path.join(BASE_DIR, "driver", "linux", "chromedriver")             # google browser
LINUX_FIREFOXDRIVER = os.path.join(BASE_DIR, "driver", "linux", "geckodriver")             # firefox browser

# browser driver path of windows
IE_PATH = os.path.join(BASE_DIR, "driver", "windos", "IEDriverServer.exe")                 # ie
WIN_CHROMEDRIVER = os.path.join(BASE_DIR, "driver", "windos", "chromedriver.exe")          # chrome
WIN_FIREFOXDRIVER = os.path.join(BASE_DIR, "driver", "windos", "geckodriver.exe")          # firefox

# log path
LOG_DIR = os.path.join(BASE_DIR, "log")

# testing case path
CASE_DIR = os.path.join(BASE_DIR, "testcase", )

# yaml path of testing data and locator data
CASE_YMAL_DIR = os.path.join(BASE_DIR, "data", "case", )                                   # testing data
LOCATOR_YMAL_DIR = os.path.join(BASE_DIR, "data", "locator", )                             # locator data

# testing file path
DATA_FILE = os.path.join(BASE_DIR, "data", "FILE")

# assert path of testing pic
DIFF_IMGPATH = os.path.join(BASE_DIR, "database", "file", "img")

# result path
RESULT_JSON_DIR = os.path.join(BASE_DIR, "result", "report_json")                          # json
RESULT_ALLURE_DIR = os.path.join(BASE_DIR, "result", "report_allure")                      # allure report
RESULT_SCREEN_DIR = os.path.join(BASE_DIR, "result", "report_screen")                      # screen result
RESULT_TEMP_DIR = os.path.join(BASE_DIR, "result", "report_temp")                          # temp dir

# project setting
SETTING_YAML_DIR = os.path.join(BASE_DIR, "config", "setting.yaml")







