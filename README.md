# 1. Project Info
## 1.1. Project catalog
common
    - common.py （logger,deleteReport）
    - driver_init.py (initialize driver)
    - read_data.py (read data from yaml or excel)
    - web_base.py (web methods)
config
    - setting.yaml (project config)
data
    - case (testing data)
    - locator (locate data)
driver
    - linux
    - windows
    - mac
log (log file)
page_object
    - page_object
result (testing result)
testcase (test scripts)
    

# 2. How to use the project

```bash
# install dependencies based on python3, python3.8 and above is recommended
pip install -r requirements.txt

# install allure
# download from https://github.com/allure-framework/allure2/releases
# add the environment variable
allure --version # see if it works

# run
python3 run.py
```
# 3. Remark