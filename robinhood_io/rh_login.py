from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from getpass import getpass

import time

timeout = 5 #seconds

#-----
def rh_login(driver):
    driver.get('https://robinhood.com/login')

    u_input, p_input = auth_input()

    driver.find_element_by_xpath("//input[@name='username']").send_keys(u_input)
    driver.find_element_by_xpath("//input[@name='password']").send_keys(p_input)
    driver.find_element_by_xpath("//button[@type='submit']").click()

    time.sleep(timeout)
    return

def auth_input():
    print('Enter your Robinhood credentials -')
    u_input = input('Email: ')
    p_input = getpass('Password: ')

    return u_input, p_input

#-----
def test_login(driver):
    driver.get('https://robinhood.com/')

    try:
        loaded = EC.presence_of_element_located((By.ID, 'fb-root'))     #'fb-root' id exclusive to pages after sign-in
        WebDriverWait(driver, timeout).until(loaded)
        print('--Login successful--')
    except TimeoutException:
        retry = input('Login failure - try again? (yes/no): ')
        if retry == 'yes':
            rh_login(driver)
            return
        else:
            print('Timeout in loading page after login')
            return
