# Adapted from https://github.com/dongKenny/artveeScraper
import csv
import json
import logging
import math
import os
import re
import requests
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import shutil
import textwrap
from unidecode import unidecode
from bs4 import BeautifulSoup

CHARS = ',."'
CHARS_NAME = " ()';`"
font_path = "./atwriter.ttf"
data_path = "./backk"
PAGES = [1, 2]
NUM_IMAGES = 20


def remove_weird_chars(string, chars):
    for c in chars:
        string = string.replace(c, "")
    return string


def create_json(csv_path, json_path):
    """
    Args:
        csv_path : file path for the csv
        json_path: file path for the json

    Explanation:
        Reads the csv and converts to a dictionary
        Uses json.dumps() to dump the data and write to json
    """

    data = {}
    with open(csv_path, encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)

        # Convert each row into a dictionary and add it to data
        for rows in csv_reader:
            key = rows['Title']
            data[key] = rows

    with open(json_path, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

# Function to overlay title and artist on image
def overlay_text(img_path, title, artist):
    try:
        img = Image.open(img_path).convert("RGBA")
    except UnidentifiedImageError:
        print("Could not read", img_path)
        return 
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 30)
    text_width, text_height = draw.textsize(title, font)
    text_width2, text_height2 = draw.textsize(artist, font)
    
    # Create a rectangle with alpha 0.8
    TINT_COLOR = (0, 0, 0)
    TRANSPARENCY = 0.55
    OPACITY = int(255 * TRANSPARENCY)
    overlay = Image.new('RGBA', img.size, TINT_COLOR+(0,))
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
    
    draw.rectangle([(0, img.height-text_height-text_height2-5),
                   (max(text_width, text_width2), img.height)], fill=TINT_COLOR+(OPACITY,))
    
    if text_width > img.width:
        title_lines = textwrap.wrap(title, width=int(
            img.width/font.getsize(title)[0]*font.getsize(title)[1]))
        for i, line in enumerate(title_lines):
            draw.text((0, img.height-text_height*(len(title_lines)+1)),
                      line, font=font, fill=(255, 255, 255, 255))
    else:
        draw.text((0, img.height-text_height-text_height2),
                  title, font=font, fill=(255, 255, 255, 255))

    if text_width2 > img.width:
        artist_lines = textwrap.wrap(artist, width=int(
            img.width/font.getsize(artist)[0]*font.getsize(artist)[1]))
        for i, line in enumerate(artist_lines):
            draw.text((0, img.height-text_height2*(len(artist_lines)+1)),
                      line, font=font, fill=(255, 255, 255, 255))
    else:
        draw.text((0, img.height-text_height2), artist,
                  font=font, fill=(255, 255, 255, 255))

    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB") # Remove alpha for saving in jpg format.
    # Save the image
    print("Saving to", img_path)
    img.save(img_path)


def scrape_images(img_source, img_index, title, data_path):
    """
    Args:
        img_source : list of the 'a' elements which direct to the image download options
        img_index (int): the current image out of the NUM_IMAGES cards on the page
        title (str): name of the artwork used in the file name

    Explanation:
        Finds the page to download images using the href in an element of img_source
        Parses the download page and uses soup to get the download link for the image
    """
    img_dl_page = img_source[img_index]
    img_soup = BeautifulSoup(str(img_dl_page), "html.parser")
    img_tag = img_soup.img
    img_filename = img_tag['src'].split('/')[-1]
    img_filename = img_filename.split('.')
    img_filename = img_filename[0] + 'sdl.' + img_filename[1]
    
    img_link = "https://mdl.artvee.com/sdl/" + img_filename
    title = ''.join([i for i in title if i.isalpha()])
    img_path = os.path.join(data_path, title + ".jpg")
    
    
    if os.path.exists(img_path):
        return None
        
    print("Downloading", img_link)
    response = requests.get(img_link, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    img_file = open(img_path, 'wb')
    shutil.copyfileobj(response.raw, img_file)
    img_file.close()

    return img_path


def scrape_meta_images(url, category, data_path, writer):
    """
    Args:  
        url (str): URL for the paginated category pages
        category (str): The category used in the url
        data_path (str): The path where the csv, json, and temporary images will be stored
        writer: Writes the appended elements in data to the csv

    Explanation:
        Parses the page of NUM_IMAGES artworks and puts cards, which contain the image and metadata, in a list
        Parses the page for the image download page to be passed in after scraping metadata
        In each card, finds the title and artist and appends to data []
        Scrapes the image 
        Writes data to the csv and moves to the next card
    """

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    cards = soup.find_all("div", {"class": re.compile(
        "product-grid-item product woodmart-hover-tiled*")})
    img_source = soup.find_all(
        "div", {"class": "product-element-top product-image-link pttl tbmc linko"})
    img_index = 0

    for card in cards:
        data = []

        # Formatted in nested if-statements to prevent receiving an error for a missing element/class (None type)
        title = card.find("h3", class_="product-title")
        if (title != None):
            if (title.find("a") != None):
                title = title.get_text()
                title = remove_weird_chars(title, CHARS)
                data.append(title)
        else:
            title = "Untitled"
            data.append(title)

        artist_info = card.find("div", class_="woodmart-product-brands-links")
        if (artist_info != None):
            artist_info = artist_info.get_text()
            artist_info = remove_weird_chars(artist_info, CHARS)
            data.append(artist_info)
        else:
            artist_info = "Unknown"
            data.append(artist_info)

        data.append(category)

        img_path = scrape_images(img_source, img_index, title, data_path)
        data.append(img_path)
        
        title = unidecode(title)
        
        if img_path is not None:
            overlay_text(img_path, title, artist_info)
            writer.writerow(data)
            
        img_index += 1


def count_pages(category):
    """
    Args:
        category : used in the url to find the page and its respective results

    Explanation:
        Parse first page of a category
        Find number of results displayed on page
        Have NUM_IMAGES results displayed, mod NUM_IMAGES, and add 1 for any remainder
        Return total number of pages to iterate through
    """

    url = "https://artvee.com/c/%s/page/1/?per_page=%i" % (category, NUM_IMAGES)
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("p", class_="woocommerce-result-count")
    print(results.text)
    results = results.text.strip("items").strip()

    no_pages = math.floor(int(results) / NUM_IMAGES)

    if (int(results) % NUM_IMAGES > 0):
        no_pages += 1

    return no_pages


def get_categories():
    url = "https://artvee.com"
    response = requests.get(url)

    # Parse the html content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the ul element with class "sub-menu color-scheme-dark"
    menu_element = soup.find('ul', {'class': 'sub-menu color-scheme-dark'})

    # Extract all the li elements within the ul element
    menu_items = menu_element.find_all('li')

    # Extract the text within the 'span' elements of each li element
    return [item.find('span', {'class': 'nav-link-text'}).text.replace(' ', '-') for item in menu_items]


if __name__ == "__main__":
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    
    csv_path = os.path.join(data_path, "artvee.csv")
    json_path = os.path.join(data_path + "artvee.json")
    
    if (data_path == ""):
        print("\nPlease assign a value to the data_path\n")
        exit(-1)
        
    first_edit = True   
    
    if os.path.exists(csv_path):
        first_edit = False

    f = open(csv_path, "a", encoding="utf-8")

    # Create csv writer and header row
    writer = csv.writer(f)

    if first_edit:
        headers = ["Title", "Artist", "Category", "Path"]
        writer.writerow(headers)

    # Artvee categorizes its works and these are how they are written in the url
    categories = get_categories()
    print(categories)
    
    for category in categories:
        no_pages = count_pages(category)

        # Pagination
        for p in PAGES:
            if p < no_pages:
                print("Currently looking at: %s, page %d" % (category, p))
                url = "https://artvee.com/c/%s/page/%d/?per_page=NUM_IMAGES" % (
                    category, p)
                scrape_meta_images(url, category, data_path, writer)

    f.close()
