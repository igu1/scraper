import requests
from bs4 import BeautifulSoup
import utils.image as image
from utils.webAccess import WebAccess
import os
import argparse


class DataGather:
    def __init__(self, name):
        self.name = name

    def get_info(self, web_access: WebAccess):
        web_access.searchInGoogle(self.name)
        sites = web_access.searchForSiteInGoogle()
        for site in sites:
            web_access.extractData(site, self.name)
        image.create_image(self.name, 2)


def main():
    parser = argparse.ArgumentParser(description="Description of your program")
    parser.add_argument(
        "-t", type=int, help="About of thread / Amount of Chrome instances"
    )
    parser.add_argument("-d", type=str, help=".txt path of names")
    args = parser.parse_args()

    web_access = WebAccess(dictionary="data/")

    requests = []

    try:
        with open(args.d or "data.txt", "r") as file:
            requests = file.read().splitlines()
    except FileNotFoundError:
        print(
            f"{args.d or 'data.txt'}.txt not found. Please add data to {args.d or 'data.txt'}."
        )

    if not requests:
        input_request = input("Enter name: ")
        request = DataGather(input_request)
        request.get_info(web_access)
    else:
        for input_request in requests:
            request = DataGather(input_request)
            request.get_info(web_access)


if __name__ == "__main__":
    main()
