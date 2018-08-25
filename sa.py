from robinhood_io.rh_navigate import rh_login, test_login, rh_open
from robinhood_io.rh_debug import debug_mode, continue_mode                 #remove any if obsolete
from stock_io.stock_mgmt import stock_requests                              #uses Stock class
from forecast_io.forecast_collect import get_stock_intraday
from selenium import webdriver

import os

#-----

def entry(driver):

    rh_login(driver=driver)
    test_login(driver=driver)


#-----

def main():
    driver = webdriver.Chrome(os.getcwd() + '/robinhood_io/chromedriver')

    entry(driver)                                                                   #login and test login

    sa_requests = stock_requests()                                                  #request and store from user inputs
    rh_open(driver, sa_requests)                                                    #open each stock in a new tab
    sa_data = {req.symbol:get_stock_intraday(req.symbol) for req in sa_requests}    #collect intraday data into a dict
    

if __name__ == '__main__':
    main()
