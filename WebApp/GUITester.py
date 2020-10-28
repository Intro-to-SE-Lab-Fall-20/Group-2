from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager #must pip install webdriver_manager
from selenium.webdriver.common.keys import Keys
import time

def login():
    userName = driver.find_element_by_xpath('//*[@id="inputEmail"]')
    userName.send_keys("group2emailclient@gmail.com")

    password = driver.find_element_by_xpath('//*[@id="inputPassword"]')
    password.send_keys("Group2Test")

    login = driver.find_element_by_xpath("/html/body/form/button")
    login.click()

def sendEmail():

    sendMail = driver.find_element_by_xpath('//*[@id="sendmail"]')
    sendMail.click()

    to = driver.find_element_by_xpath('//*[@id="sendto"]')
    to.send_keys("group2emailclient@gmail.com")

    time.sleep(1)

    subject = driver.find_element_by_xpath('//*[@id="subject"]')
    subject.send_keys("Test subject", Keys.TAB, "Test Body")

    send = driver.find_element_by_xpath('//*[@id="myForm"]/form/button[1]')
    send.click()

def forward():
    email = driver.find_element_by_xpath('/html/body/div/table/tbody/tr[1]')
    email.click()

    forward = driver.find_element_by_id('forward')
    time.sleep(1)
    forward.click()

    to = driver.find_element_by_xpath('//*[@id="sendto"]')
    to.send_keys("group2emailclient@gmail.com")
    time.sleep(1)

    send = driver.find_element_by_xpath('//*[@id="myForm"]/form/button[1]')
    send.click()

def checkForward():
    email = driver.find_element_by_xpath('/html/body/div/table/tbody/tr[1]')
    email.click()

    time.sleep(3) #showing email was forwarded

    cancel = driver.find_element_by_id('cancel')
    cancel.click()

def logout():
    logout = driver.find_element_by_xpath('/html/body/div/form[1]/button')
    logout.click()

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    driver.get("http://0.0.0.0:5000")

    login()
    time.sleep(1) #pause for browser to load
    sendEmail()
    time.sleep(3) #pause on inbox to show sent email
    forward()
    time.sleep(3) #pause on inbox to show forwarded email
    checkForward()
    time.sleep(1)
    logout()
