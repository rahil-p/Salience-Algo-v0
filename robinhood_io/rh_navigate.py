from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from getpass import getpass

import time

timeout0 = 1 #seconds
timeout1 = 5 #seconds
timeout2 = 10 #seconds

#-----
def rh_login(driver):
    print('--Welcome to Sentience--')
    driver.get('https://robinhood.com/login')

    u_input, p_input = auth_input()

    driver.find_element_by_xpath("//input[@name='username']").send_keys(u_input)
    driver.find_element_by_xpath("//input[@name='password']").send_keys(p_input)
    driver.find_element_by_xpath("//button[@type='submit']").click()

    time.sleep(timeout1)
    return u_input

def auth_input():
    print('--Log in for Sentience--')
    print('Enter your Robinhood credentials -')
    u_input = input('Email: ')
    p_input = getpass('Password: ')

    return u_input, p_input

def test_login(driver):
    try:
        loaded = EC.presence_of_element_located((By.ID, 'fb-root'))     #'fb-root' id exclusive to pages after sign-in
        WebDriverWait(driver, timeout2).until(loaded)
        print('--Login successful--')
    except TimeoutException:
        retry = input("Login failure - type 'yes' to try again: ")
        if retry == 'yes':
            rh_login(driver)
            return
        else:
            print('Timeout in loading page after login')
            exit()

#-----

def rh_open(driver, stocks_array):
    for stock in stocks_array:
        driver.execute_script("window.open('https://robinhood.com/" +
                                           stock.type + "/" +
                                           stock.symbol +
                                           "');")
