import contextlib
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime


class WebAccess:
    # Attributes:
    #     driver: The web driver for accessing websites.
    #     wiki (bool): Whether to include 'wikipedia' in search requests.
    #     dictionary (str): The directory to save extracted data.

    # Methods:
    #     searchInGoogle(request): Searches for a request in Google.
    #     searchinSite(request): Searches for a request in a specific website.
    #     searchForSiteInGoogle() -> list: Searches for a website in Google and returns a list of sites.
    #     extractData(site, request) -> None: Extracts data from a website and saves it to a file.
    #     closeBrowser(): Closes the web browser.
    def __init__(self, wiki=True, dictionary=os.curdir):
        self.driver = webdriver.Chrome()
        self.wiki = wiki
        self.dictionary = dictionary

    def searchInGoogle(self, request):
        if self.wiki:
            request = f"{request} wikipedia"
        self.driver.get(
            f"https://www.google.com/search?q={request}&uact=5&oq={request}&sclient=gws-wiz"
        )

    def searchinSite(self, request):
        self.driver.get(f"https://www.{request}.com")

    def searchForSiteInGoogle(self) -> list:
        try:
            all_ref = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'MjjYud')]"
            )
            sites = []
            for ref in range(1, len(all_ref)):
                with contextlib.suppress(NoSuchElementException):
                    site = (
                        all_ref[ref]
                        .find_element(
                            By.XPATH,
                            f"//*[@id='rso']/div[{ref}]/div/div/div[1]/div/div/span/a",
                        )
                        .get_attribute("href")
                    )
                    if site.startswith("https://"):
                        sites.append(site)
            return sites

        except Exception as e:
            print("An error occurred:", e)

    def extractData(self, site, request) -> None:
        if not request:
            print("No Search Name Found...")
            return
        text_file_name = re.sub(
            r"\W+", "_", os.path.basename(site.strip().strip('"').strip("'"))
        )
        is_exist = os.path.exists(
            os.path.join(self.dictionary, request, text_file_name)
        )
        print(
            f"[\033[92m{datetime.now().strftime('%y-%m-%d ')}{datetime.now().strftime('%H:%M:%S')}\033[0m] Scanning Data from site: "
            + site
            + f" for {request}..."
        )
        try:
            if "wikipedia" not in site:
                print("Not a wikipedia site")
                return
            self.driver.get(site)
            response = self.driver.page_source
            soup = BeautifulSoup(response, "html.parser")
            main_content_div = soup.find("div", {"class": "mw-content-ltr"})
            file_path = os.path.join(
                self.dictionary,
                request,
                f"{text_file_name}.txt",
            )
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "a", encoding="utf-8") as file:
                try:
                    paragraphs = main_content_div.find_all("p")
                    for paragraph in paragraphs:
                        file.write(paragraph.text)
                except Exception as e:
                    print("Error writing to file:", e)

        except FileNotFoundError:
            os.makedirs("data")
            os.makedirs(f"data/{request}")
            print("Created new directory")

    def closeBrowser(self):
        self.driver.close()
