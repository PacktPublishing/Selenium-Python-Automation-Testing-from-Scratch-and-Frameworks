def test_screenshot_on_test_failure(browser):
    # driver = webdriver.Firefox()
    browser.get("https://google.com")
    assert 2 ==3