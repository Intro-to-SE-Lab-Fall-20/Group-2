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

    subject = driver.find_element_by_xpath('//*[@id="subject"]')
    subject.send_keys("Test subject", Keys.TAB, "Test Body")

    send = driver.find_element_by_xpath('//*[@id="myForm"]/form/button[1]')
    send.click()

def logout():
    logout = driver.find_element_by_xpath("/html/body/div/form[1]")
    logout.click()

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    driver.get("http://0.0.0.0:5000")

    login()
    sendEmail()
    time.sleep(3) #pause on inbox to show sent email
    logout()
