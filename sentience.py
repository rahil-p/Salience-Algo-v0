from robinhood_io.rh_navigate import rh_login, test_login, rh_open
from robinhood_io.rh_debug import debug_mode                                #remove any if obsolete
from stock_io.stock_mgmt import stock_requests                              #uses Stock class
from forecast_io.forecast_preprocess import get_stock_intraday
from forecast_io.forecast_plot import plotly_set_credentials, make_plot
from forecast_io.forecast_nn import *                                       #must be changed to import specifics
from communication_io.email_sends import pre_send, post_send
from selenium import webdriver

import os
#import sched
#import time
from datetime import datetime, timedelta

#-----
def entry(driver):
    email = rh_login(driver=driver)
    test_login(driver=driver)

    return email

#-----
def get_closing_time():
    now = datetime.now()
    closing_seconds = (timedelta(hours=24) -
                       (now - now.replace(hour=17, minute=10, second=0))).total_seconds() % (24 * 3600)

    return now, closing_seconds

def pre_open(to_email, requests_array):
    _, closing_seconds = get_closing_time()
    pre_email_sent = False
    switch = 1
    while closing_seconds >= 23400:
        _, closing_seconds = get_closing_time()
        if switch == 1:
            switch *= 0
            pre_email_sent = pre_send(to_email, requests_array)
            print('--Sentience will execute at market open, 9:30am--')
        else:
            pass
    return pre_email_sent

def during_hours(pre_email_sent, to_email, requests_array):
    _, closing_seconds = get_closing_time()
    if pre_email_sent == False:
        pre_email_sent = pre_send(to_email, requests_array)
    switch = 1
    while closing_seconds in range(30, 23400):
        _, closing_seconds = get_closing_time()
        if switch == 1:
            switch *= 0
            print('--Sentience is now active--')
        #do all other stuff

def at_close(to_email, requests_array):
    _, closing_seconds = get_closing_time()
    if closing_seconds < 30:
        print('--Sentience trading session has completed--')
        post_send(to_email, requests_array)

#if pre open, send pre_send on pre_open
#if during hours, send pre_send on during_hours
#


#-----
def main():
    driver = webdriver.Chrome(os.getcwd() + '/robinhood_io/chromedriver')

    email = entry(driver)                                                           #login and test login

    sa_requests = stock_requests(driver)                                            #request and store from user inputs
    rh_open(driver, sa_requests)                                                    #open each stock in a new tab
    #sa_data = {req.symbol:[get_stock_intraday(req.symbol),                          #collect intraday data into a dict
    #                       make_plot(get_stock_intraday(req.symbol), req.symbol)] for req in sa_requests}
    for request in sa_requests:
        request.pre_data, _ = get_stock_intraday(request.symbol)
        request.pre_plot = make_plot(request.pre_data, request.symbol)
    print(sa_requests[0].pre_plot)

    #-----
    pre_email_sent = pre_open(email, sa_requests)
    during_hours(pre_email_sent, email, sa_requests)
    at_close(email, sa_requests)

if __name__ == '__main__':
    main()


#create testing script for forecast + trading decisions & develop
#visualize forecasts (noting transaction moments/summaries)

#email at closing for summary

#handle buy/sell functions
#handle buy/sell confirmations
#handle errors - check buying power

#handle requirements
#include crypto support
