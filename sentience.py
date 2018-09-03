from robinhood_io.rh_navigate import rh_login, test_login, rh_open
from robinhood_io.rh_debug import debug_mode                                #remove any if obsolete
from stock_io.stock_mgmt import stock_requests                              #uses Stock class
from forecast_io.forecast_preprocess import get_stock_intraday
from forecast_io.forecast_plot import plotly_set_credentials, make_plot
from forecast_io.forecast_lstm import *                                       #must be changed to import specifics
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

def set_stock_properties(requests_array):
    for request in requests_array:
        request.data, _ = get_stock_intraday(request.symbol)
        request.plot = make_plot(request.data, request.symbol)

def update_stock_properties(requests_array):
    for request in requests_array:
        tmp_pd, _ = get_stock_intraday(request.symbol, outputsize=10,
                                       starting_date=request.data['date'].min())            #get last 10 datapoints
        tmp_updated = request.data.merge(tmp_pd, on=list(request.data), how='outer')        #merge the datapoints
        tmp_updated.drop_duplicates(subset=['date'], inplace=True, keep='last')             #drop duplicate datapoints

        request.data = tmp_updated                                                          #update object properties
        request.plot = make_plot(request.data, request.symbol)

    return


#-----
def get_closing_time():
    now = datetime.now()
    closing_seconds = (timedelta(hours=24) -
                       (now - now.replace(hour=1, minute=42, second=0))).total_seconds() % (24 * 3600)

    return now, closing_seconds

#-
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

#-
def during_hours(pre_email_sent, to_email, requests_array):
    now, closing_seconds = get_closing_time()
    if pre_email_sent == False:
        pre_email_sent = pre_send(to_email, requests_array)
    switch = 1

    while closing_seconds in range(30, 23400):
        last_minute = now.minute
        now, closing_seconds = get_closing_time()

        #executes at the initiation of the loop (just once)
        if switch == 1:
            switch *= 0
            print('--Sentience is now active--')
            update_stock_properties(requests_array)

        #executes at each new minute; ensures that alpha_vantage data is not requested more than once per minute
        if now.minute != last_minute:
            update_stock_properties(requests_array)

        #predict
        #buy/sell

#-
def at_close(to_email, requests_array):
    _, closing_seconds = get_closing_time()
    if closing_seconds < 30:
        print('--Sentience trading session has completed--')
        post_send(to_email, requests_array)






#-----
def main():
    driver = webdriver.Chrome(os.getcwd() + '/robinhood_io/chromedriver')

    email = entry(driver)                                                           #login and test login

    sa_requests = stock_requests(driver)                                            #request and store from user inputs
    rh_open(driver, sa_requests)                                                    #open each stock in a new tab

    set_stock_properties(sa_requests)

    #-----
    pre_email_sent = pre_open(email, sa_requests)
    during_hours(pre_email_sent, email, sa_requests)
    print(sa_requests[0].data)
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
