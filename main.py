import requests
from bs4 import BeautifulSoup
import utils.image as image
from utils.webAccess import WebAccess
import os
import argparse
import threading
import re


def sanitized_request(request):
    return re.sub(r'[<>:"/\\|?*]', "_", request)


def split_list_into_chunks(lst, num_chunks):
    avg_chunk_size = len(lst) // num_chunks
    return [lst[i : i + avg_chunk_size] for i in range(0, len(lst), avg_chunk_size)]


class DataGather:
    def __init__(self, name):
        self.name = name

    def get_info(self, web_access: WebAccess):
        web_access.searchInGoogle(self.name)
        sites = web_access.searchForSiteInGoogle()
        for site in sites:
            web_access.extractData(site, self.name)
        image.create_image(self.name, 2)


def process_data_chunk(web_access_instances, data_chunk, instance_index):
    web_access_instance = web_access_instances[instance_index]
    for name in data_chunk:
        name = sanitized_request(name)
        dg = DataGather(name)
        dg.get_info(web_access_instance)


def main():
    parser = argparse.ArgumentParser(description="Web Scraping Tool")
    parser.add_argument(
        "-t", type=int, help="Number of threads / Amount of Chrome instances"
    )
    parser.add_argument("-d", type=str, help=".txt path of names")
    args = parser.parse_args()

    no_of_threads = args.t or 1

    web_access_instances = [
        WebAccess(dictionary=os.curdir) for _ in range(no_of_threads)
    ]

    data = []

    try:
        with open(args.d or "data.txt", "r") as file:
            data = file.read().splitlines()
    except FileNotFoundError:
        print(
            f"{args.d or 'data.txt'}.txt not found. Please add data to {args.d or 'data.txt'}."
        )
        return

    data_chunks = split_list_into_chunks(data, no_of_threads)

    threads = []
    for i, chunk in enumerate(data_chunks):
        thread = threading.Thread(
            target=process_data_chunk, args=(web_access_instances, chunk, i)
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for web_access_instance in web_access_instances:
        web_access_instance.closeBrowser()


if __name__ == "__main__":
    main()
