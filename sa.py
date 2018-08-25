from robinhood_io.rh_navigate import rh_login, test_login, rh_open
from robinhood_io.rh_debug import debug_mode, continue_mode                 #remove any if obsolete
from stock_io.stock_mgmt import stock_requests                              #uses Stock class
from selenium import webdriver

import os

#-----

def entry(driver):

    rh_login(driver=driver)
    test_login(driver=driver)


#-----

def main():
    driver = webdriver.Chrome(os.getcwd() + '/robinhood_io/chromedriver')

    entry(driver)

    sa_requests = stock_requests()
    rh_open(driver, sa_requests)


if __name__ == '__main__':
    main()
