from selenium import webdriver

driver = webdriver.Chrome(executable_path='/Users/elihartnett/Desktop/tester/chromedriver')
driver.get("http://192.168.0.155:5000")

userName = driver.find_element_by_xpath('//*[@id="inputEmail"]')
userName.send_keys("group2emailclient@gmail.com")

password = driver.find_element_by_xpath('//*[@id="inputPassword"]')
password.send_keys("Group2Test")

login = driver.find_element_by_xpath("/html/body/form/button")
login.click()

sendMail = driver.find_element_by_xpath("/html/body/div/button")
sendMail.click()

to = driver.find_element_by_xpath('//*[@id="sendto"]')
to.send_keys("elichartnett@gmail.com")

subject = driver.find_element_by_xpath("/html/body/form/input[2]")
subject.send_keys("Test subject")

body = driver.find_element_by_xpath("/html/body/form/textarea")
body.send_keys("Test body")

send = driver.find_element_by_xpath("/html/body/form/button")
send.click()

print("done")
