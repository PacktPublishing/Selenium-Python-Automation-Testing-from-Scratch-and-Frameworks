from selenium import webdriver
from selenium.webdriver.support.select import Select

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("headless")
chrome_options.add_argument("--ignore-certificate-errors")


driver = webdriver.Chrome(executable_path="C:\\chromedriver.exe",options=chrome_options)

driver.get("https://rahulshettyacademy.com/angularpractice/")

print(driver.title)