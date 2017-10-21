from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import pytest
import re

MAX_WAIT = 10

@pytest.fixture(scope="module")
def browser(request):
    """Firefox browser object factory === pytest fixture
    for the firefox browser
    """
    firefox_browser = webdriver.Firefox()

    def close_browser():
        """teardown method for closing browser after test"""
        firefox_browser.quit()

    request.addfinalizer(close_browser)

    return firefox_browser

# NEW VISITOR TEST
def wait_for_row_in_list_table(browser, row_text):
    start_time = time.time()
    while True:
        try:
            table = browser.find_element_by_id('id_list_table')
            rows = table.find_elements_by_tag_name('tr')
            assert row_text in [row.text for row in rows]
            return
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.5)

def test__can_start_a_list_for_one_user(browser, live_server):
    # Edith has heard about a cool new online to-do app. 
    # She goes to check out its homepage
    browser.get(live_server.url)

    # She notices the page title and header mention to-do lists
    assert 'To-Do' in browser.title
    header_text = browser.find_element_by_tag_name('h1').text
    assert 'To-Do' in header_text

    # She is invited to enter a to-do item straight away
    inputbox = browser.find_element_by_id('id_new_item')
    assert inputbox.get_attribute('placeholder') == 'Enter a to-do item'

    # She types "Buy peacock feathers" into a text box (Edith's hobby
    # is tying fly-fishing lures)
    inputbox.send_keys('Buy peacock feathers')

    # When she hits enter, the page updates, and now the page lists
    # "1: Buy peacock feathers" as an item in a to-do list
    inputbox.send_keys(Keys.ENTER)
    wait_for_row_in_list_table(browser, '1: Buy peacock feathers')

    # There is still a text box inviting her to add another item.
    # She enters "Use peacock feathers to make a fly" (Edith is very methodical)
    inputbox = browser.find_element_by_id('id_new_item')
    inputbox.send_keys('Use peacock feathers to make a fly')
    inputbox.send_keys(Keys.ENTER)

    # The page updates again, and now shows both items on her list
    wait_for_row_in_list_table(browser, '1: Buy peacock feathers')
    wait_for_row_in_list_table(browser, '2: Use peacock feathers to make a fly')

    # Satisfied, she goes back to sleep

def test__layout_and_styling(browser, live_server):
    # Edith goes to the home page
    browser.get(live_server.url)
    browser.set_window_size(1024, 768)

    # She notices the input box is nicely centered
    inputbox = browser.find_element_by_id('id_new_item')
    assert abs(512 - (inputbox.location['x'] + inputbox.size['width'] / 2)) < 10

def test__multiple_users_can_start_lists_at_different_urls(browser, live_server):
    # Edith starts a new to-do list
    browser.get(live_server.url)
    inputbox = browser.find_element_by_id('id_new_item')
    inputbox.send_keys('Buy peacock feathers')
    inputbox.send_keys(Keys.ENTER)
    wait_for_row_in_list_table(browser, '1: Buy peacock feathers')

    # She notices that her list has a unique URL
    edith_list_url = browser.current_url
    assert re.compile('.*/lists/.+').match(edith_list_url)

    # Now a new user, Francis, comes along to the site

    ## We use a new browser session to make sure that no information
    ## of Edith's is coming through fromm cookies etc
    browser.quit()
    browser = webdriver.Firefox()

    # Francis visits the home page. There is no sign of Edith's list
    browser.get(live_server.url)
    page_text = browser.find_element_by_tag_name('body').text
    assert 'Buy peacock feathers' not in page_text
    assert 'make a fly' not in page_text

    # Francis starts a new list by entering a new item. he is
    # less intersting than Edith...
    inputbox = browser.find_element_by_id('id_new_item')
    inputbox.send_keys('Buy milk')
    inputbox.send_keys(Keys.ENTER)
    wait_for_row_in_list_table(browser, '1: Buy milk')

    # Francis gets his own unique URL
    francis_list_url = browser.current_url
    assert re.compile('.*/lists/.+').match(francis_list_url)
    assert francis_list_url != edith_list_url

    # Again. there is no trace of Edith's list
    page_text = browser.find_element_by_tag_name('body').text
    assert 'Buy peacock feathers' not in page_text
    assert 'Buy milk' in page_text

    # Satisfied, they both go back to sleep
    browser.quit()
