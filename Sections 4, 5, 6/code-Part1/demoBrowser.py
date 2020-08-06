from selenium import webdriver
#browser exposes an executable file
#Through Selenium test we need to invoke the executable file which will then invoke actual browser
#driver = webdriver.Chrome(executable_path="C:\\chromedriver.exe")
#driver=webdriver.Firefox(executable_path="C:\\geckodriver.exe")
driver = webdriver.Ie(executable_path="C:\\IEDriverServer.exe")
driver.maximize_window()
driver.get("https://rahulshettyacademy.com/")  #get method to hit url on  browser

print(driver.title)
print(driver.current_url)
driver.get("https://rahulshettyacademy.com/AutomationPractice/")
driver.minimize_window()
driver.back()
driver.refresh()
driver.close()









