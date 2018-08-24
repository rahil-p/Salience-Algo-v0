from robinhood_io.rh_login import rh_login, test_login
from robinhood_io.rh_debug import debug_mode, continue_mode
from selenium import webdriver
import os

def login():
    driver = webdriver.Chrome(os.getcwd() + '/robinhood_io/chromedriver')

    rh_login(driver=driver)
    test_login(driver=driver)
    continue_mode()



if __name__ == '__main__':
    login()
