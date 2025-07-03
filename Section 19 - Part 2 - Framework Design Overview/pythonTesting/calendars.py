import time

from selenium import webdriver
from selenium.webdriver.common.by import By

monthNumber = "6"
date = "15"
year = "2027"
expectedList = [monthNumber, date, year]
driver = webdriver.Chrome()
driver.get("https://rahulshettyacademy.com/seleniumPractise/#/offers")
driver.implicitly_wait(5)

# Interacting with calendar
driver.find_element(By.CSS_SELECTOR,".react-date-picker__inputGroup").click()
driver.find_element(By.CSS_SELECTOR,".react-calendar__navigation__label").click();
driver.find_element(By.CSS_SELECTOR,".react-calendar__navigation__label").click();

driver.find_element(By.XPATH,"//button[text()='"+year+"']").click()

driver.find_elements(By.CSS_SELECTOR,".react-calendar__year-view__months__month")[int(monthNumber)-1].click()
driver.find_element(By.XPATH,f"//abbr[text()='{date}']").click()

actualList = driver.find_elements(By.CSS_SELECTOR,".react-date-picker__inputGroup__input ")
for i in range(len(actualList)):
    print(actualList[i].get_attribute("value"))
    assert actualList[i].get_attribute("value") == expectedList[i]
























