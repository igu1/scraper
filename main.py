import requests
from bs4 import BeautifulSoup
import utils.image as image
from utils.webAccess import WebAccess
import os


def get_character_info(web_access: WebAccess, request):
    web_access.searchInGoogle(request)
    sites = web_access.searchForSiteInGoogle()
    for site in sites:
        web_access.extractData(site, request)
    image.create_image(request, 2)

    # Number of threads to use


web_access = WebAccess(dictonary="data/")

characters = []

try:
    with open("characters.txt", "r") as file:
        characters = file.read().splitlines()
except FileNotFoundError:
    print("characters.txt not found. Please add characters to characters.txt.")

if not characters:
    character_name = input("Enter name: ")

if characters:
    for character in characters:
        get_character_info(web_access, character)
else:
    get_character_info(web_access, character_name)
