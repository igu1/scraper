import pytest
import os
import re
from unittest.mock import MagicMock, patch, mock_open, call
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# Attempt to import WebAccess, handling potential ImportError for local testing vs. environment
try:
    from utils.webAccess import WebAccess
except ImportError:
    # This path adjustment is sometimes needed if 'utils' is not directly in PYTHONPATH
    # For example, if tests are run from the project root.
    import sys
    # os is already imported, no need to import again
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.webAccess import WebAccess


# Test class for WebAccess
class TestWebAccess:

    # Tests for searchInGoogle
    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    def test_searchInGoogle_with_wikipedia(self, mock_chrome_driver):
        web_access = WebAccess(wiki=True)
        web_access.searchInGoogle("Test Character")
        expected_url = "https://www.google.com/search?q=Test Character wikipedia&uact=5&oq=Test Character wikipedia&sclient=gws-wiz"
        web_access.driver.get.assert_called_once_with(expected_url) # Use web_access.driver

    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    def test_searchInGoogle_without_wikipedia(self, mock_chrome_driver):
        web_access = WebAccess(wiki=False)
        web_access.searchInGoogle("Test Character")
        expected_url = "https://www.google.com/search?q=Test Character&uact=5&oq=Test Character&sclient=gws-wiz"
        web_access.driver.get.assert_called_once_with(expected_url) # Use web_access.driver

    # Tests for searchForSiteInGoogle
    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    def test_searchForSiteInGoogle_extracts_links(self, mock_chrome_driver):
        web_access = WebAccess()
        # mock_chrome_driver is the mock for Chrome() instance, which is web_access.driver
        mock_driver = web_access.driver

        mock_link_element_1 = MagicMock()
        mock_link_element_1.get_attribute.return_value = "https://example.com/page1"
        mock_search_result_1 = MagicMock()
        mock_search_result_1.find_element.return_value = mock_link_element_1

        mock_link_element_2 = MagicMock()
        mock_link_element_2.get_attribute.return_value = "https://example.org/another"
        mock_search_result_2 = MagicMock()
        mock_search_result_2.find_element.return_value = mock_link_element_2

        mock_link_element_http = MagicMock()
        mock_link_element_http.get_attribute.return_value = "http://notsafe.com"
        mock_search_result_http = MagicMock()
        mock_search_result_http.find_element.return_value = mock_link_element_http

        mock_driver.find_elements.return_value = [mock_search_result_1, mock_search_result_2, mock_search_result_http]

        sites = web_access.searchForSiteInGoogle()

        web_access.driver.find_elements.assert_called_once_with(By.XPATH, "//div[contains(@class, 'MjjYud')]")

        # Check that find_element was called on each mock search result
        mock_search_result_1.find_element.assert_called_once_with(By.XPATH, ".//a[@href]")
        mock_search_result_2.find_element.assert_called_once_with(By.XPATH, ".//a[@href]")
        mock_search_result_http.find_element.assert_called_once_with(By.XPATH, ".//a[@href]")

        assert sites == ["https://example.com/page1", "https://example.org/another"]

    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    def test_searchForSiteInGoogle_no_results(self, mock_chrome_driver):
        web_access = WebAccess()
        mock_driver = web_access.driver # Get the instance of the mock driver
        mock_driver.find_elements.return_value = []

        sites = web_access.searchForSiteInGoogle()

        web_access.driver.find_elements.assert_called_once_with(By.XPATH, "//div[contains(@class, 'MjjYud')]")
        assert sites == []

    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    def test_searchForSiteInGoogle_element_not_found(self, mock_chrome_driver):
        web_access = WebAccess()
        mock_driver = web_access.driver # Get the instance of the mock driver

        mock_link_element_valid = MagicMock()
        mock_link_element_valid.get_attribute.return_value = "https://example.com/valid"
        mock_search_result_valid = MagicMock()
        mock_search_result_valid.find_element.return_value = mock_link_element_valid

        mock_search_result_invalid = MagicMock()
        mock_search_result_invalid.find_element.side_effect = NoSuchElementException("Element not found for testing")

        mock_driver.find_elements.return_value = [mock_search_result_valid, mock_search_result_invalid]

        sites = web_access.searchForSiteInGoogle()

        web_access.driver.find_elements.assert_called_once_with(By.XPATH, "//div[contains(@class, 'MjjYud')]")
        mock_search_result_valid.find_element.assert_called_once_with(By.XPATH, ".//a[@href]")
        mock_search_result_invalid.find_element.assert_called_once_with(By.XPATH, ".//a[@href]")

        assert sites == ["https://example.com/valid"]

    # Tests for extractData
    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    @patch('utils.webAccess.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_extractData_success(self, mock_file_open, mock_os_makedirs, mock_chrome_driver):
        web_access = WebAccess(dictionary="data/") # Specify a dictionary
        mock_driver = web_access.driver

        html_content = '<html><body><div class="mw-content-ltr"><p>Paragraph 1.</p><p>Another paragraph.</p></div></body></html>'
        mock_driver.page_source = html_content

        site_url = "https://en.wikipedia.org/wiki/Test_Page"
        request_name = "TestCharacter"

        web_access.extractData(site_url, request_name)

        mock_driver.get.assert_called_once_with(site_url)

        # Expected file path construction
        # os.path.basename("https://en.wikipedia.org/wiki/Test_Page") is "Test_Page"
        # re.sub(r"\W+", "_", "Test_Page") is "Test_Page" (no non-alphanumeric characters in "Test_Page" itself)
        expected_text_file_name = "Test_Page" # Corrected based on os.path.basename behavior

        # Construct expected path using os.path.join for platform independence
        expected_dir_path = os.path.join("data/", request_name)
        expected_file_path = os.path.join(expected_dir_path, f"{expected_text_file_name}.txt")

        mock_os_makedirs.assert_called_once_with(expected_dir_path, exist_ok=True)
        mock_file_open.assert_called_once_with(expected_file_path, "w", encoding="utf-8")

        # Check calls to write
        # mock_file_open().write.assert_any_call("Paragraph 1.")
        # mock_file_open().write.assert_any_call("Another paragraph.")
        # Consolidate paragraph text as it's written in a loop
        mock_file_open().write.assert_has_calls([
            call("Paragraph 1."),
            call("Another paragraph.")
        ], any_order=False)


    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open) # Mock open to ensure no file is written
    @patch('utils.webAccess.os.makedirs') # Mock makedirs
    def test_extractData_not_wikipedia(self, mock_makedirs, mock_open_file, mock_print, mock_chrome_driver):
        web_access = WebAccess()
        mock_driver = web_access.driver # Get the instance of the mock driver

        site_url = "https://www.nopedia.com/Test_Page"
        request_name = "TestCharacter"

        web_access.extractData(site_url, request_name)

        # driver.get should not be called for content fetching if it's not a wikipedia site
        # The initial print for scanning happens before the check.
        # The site URL is printed before the "Not a wikipedia site" message.
        # The check for "wikipedia" in site_url happens before driver.get(site_url)
        # So, driver.get() should not be called if it's not a wikipedia site.
        mock_driver.get.assert_not_called()


        mock_print.assert_any_call("Not a wikipedia site")
        # The "Scanning data..." print will also happen, but we are focusing on "Not a wikipedia site"
        mock_open_file.assert_not_called()
        mock_makedirs.assert_not_called() # Should not be called if not wikipedia

    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    @patch('utils.webAccess.os.makedirs') # Patched os
    @patch('utils.webAccess.datetime', new_callable=MagicMock) # Patch datetime used in print, ensure new_callable
    def test_extractData_no_content_div(self, mock_datetime_constructor, mock_os_makedirs, mock_file_open, mock_print, mock_chrome_driver):
        # mock_datetime_constructor.now.return_value.strftime.return_value = "YY-MM-DD HH:MM:SS" # For more precise print assertion if needed
        web_access = WebAccess(dictionary="data/")
        mock_driver = web_access.driver

        html_content = '<html><body><div>Some other content, but not mw-content-ltr.</div></body></html>'
        mock_driver.page_source = html_content

        site_url = "https://en.wikipedia.org/wiki/Another_Page"
        request_name = "TestCharacter"

        web_access.extractData(site_url, request_name)

        mock_driver.get.assert_called_once_with(site_url)
        mock_print.assert_any_call(f"Could not find main content div for site: {site_url}. Skipping.")

        # Ensure file path is generated and directory creation is attempted *before* content div check
        expected_dir_path = os.path.join("data/", request_name)
        # The current code in extractData creates directory and file path even if content div is not found
        # It only returns early if main_content_div is None *before* opening the file
        # Let's verify os.makedirs was called, but open and write were not.
        # Actually, the check for main_content_div being None happens *before* file path creation or os.makedirs
        # in the version of the code I am working with (after the previous subtask was completed).
        # So, if no content_div, then os.makedirs and open should not be called.

        # Re-checking the code from previous step:
        # main_content_div = soup.find("div", {"class": "mw-content-ltr"})
        # if main_content_div is None:
        #     print(f"Could not find main content div for site: {site}. Skipping.")
        #     return
        # file_path = os.path.join(...)
        # os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # with open(file_path, "w", encoding="utf-8") as file:
        # So, if main_content_div is None, it returns. Thus, no os.makedirs or open.

        mock_os_makedirs.assert_not_called()
        mock_file_open.assert_not_called()


    @patch('builtins.print')
    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock) # To avoid real driver init
    @patch('builtins.open', new_callable=mock_open)
    @patch('utils.webAccess.os.makedirs')
    def test_extractData_no_request_name(self, mock_os_makedirs, mock_file_open, mock_chrome_driver, mock_print): # Order of mocks matters if not named
        web_access = WebAccess()
        # mock_driver = web_access.driver # Not needed as driver calls shouldn't happen

        site_url = "https://en.wikipedia.org/wiki/Some_Page"

        web_access.extractData(site_url, "") # Empty request name

        mock_print.assert_any_call("No Search Name Found...")

        # Ensure no driver actions or file operations occurred
        # Accessing web_access.driver would fail if mock_chrome_driver wasn't there.
        # So we need to assert that methods on the (mocked) driver were not called.
        assert web_access.driver.get.call_count == 0
        mock_os_makedirs.assert_not_called()
        mock_file_open.assert_not_called()

    @patch('utils.webAccess.webdriver.Chrome', new_callable=MagicMock)
    @patch('utils.webAccess.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_extractData_file_path_generation(self, mock_file_open, mock_os_makedirs, mock_chrome_driver):
        # This test focuses on the filename generation and directory creation path
        web_access = WebAccess(dictionary="custom_data/") # Use a custom dictionary
        mock_driver = web_access.driver

        html_content = '<html><body><div class="mw-content-ltr"><p>Test.</p></div></body></html>'
        mock_driver.page_source = html_content

        site_url = "https://en.wikipedia.org/wiki/Complex'\" Characters & Test Page"
        request_name = "Character Name With Spaces"

        web_access.extractData(site_url, request_name)

        # Expected file path construction
        # Simpler way to get this: site_url.strip().strip('"').strip("'") -> "https://en.wikipedia.org/wiki/Complex'\" Characters & Test Page"
        # os.path.basename(...) -> "Complex'\" Characters & Test Page"
        # re.sub(r"\W+", "_", "Complex'\" Characters & Test Page") should be "Complex_Characters_Test_Page"
        expected_text_file_name = "Complex_Characters_Test_Page" # Corrected based on re.sub behavior

        expected_dir_path = os.path.join("custom_data/", "Character Name With Spaces")
        expected_file_path = os.path.join(expected_dir_path, f"{expected_text_file_name}.txt")

        mock_os_makedirs.assert_called_once_with(expected_dir_path, exist_ok=True)
        mock_file_open.assert_called_once_with(expected_file_path, "w", encoding="utf-8")
        mock_file_open().write.assert_called_once_with("Test.")
