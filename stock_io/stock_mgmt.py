from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time

timeout0 = 3 #seconds
timeout1 = 1 #seconds

#-----
class Stock:
    def __init__(self, type, symbol, cap):
        self.type = type
        self.symbol = symbol
        self.cap = cap
        self.power = cap
        self.owned = 0

    def update(type, quantity, price):
        self.power = update_power(type, quantity, price)
        self.owned = update_owned(type, quantity, price)

    def update_power(type, quantity, price):
        pass

    def update_owned(type, quantity, price):
        pass

#-----
def stock_requests(driver):
    print('--Place your requests--')

    while True:
        try:
            request_count = int(input('# of requests: '))
            if request_count <= 4:
                break
            else:
                print("Invalid response - only 4 or fewer requests may be permitted")
        except ValueError:
            print("Invalid response - please return a numeric amount no greater than 4")

    requests = [stock_request(driver) for x in range(request_count)]

    driver.get('https://robinhood.com/')

    return requests

def stock_request(driver):
    while True:
        type = input("Type ('stocks' or 'crypto'): ")
        if type in ['stocks', 'crypto']:
            break
        else:
            print("Invalid response - please return either 'stocks' or 'crypto'")

    while True:
        try:
            symbol = input('Symbol: ').upper()
            driver.get('https://robinhood.com/' + type + '/' + symbol)
            loaded = EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary']"))
            WebDriverWait(driver, timeout0).until(loaded)
            break
        except TimeoutException:
            print('Invalid response - please return the symbol for a stock available on Robinhood')

        #to-do: test for unavailable cases on Alpha Vantage if necessary (but unlikely)

    while True:
        try:
            cap = float(input('Cap (ie max spend in USD): '))
            if cap > 0:
                break
            else:
                print('Invalid response - please return a positive amount')
        except ValueError:
            print("Invalid response - please return a positive numeric amount")


    return Stock(type, symbol, cap)
