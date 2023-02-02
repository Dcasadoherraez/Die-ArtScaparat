import csv
import time
import os
from  random import randrange
from PIL import Image, ImageDraw, ImageFont

# change this to the path of your csv file
csv_path = "./back/artvee.csv"


# Function to set background
def set_background(path):
    os.system("gsettings set org.gnome.desktop.background picture-uri file://" + path)


if __name__ == "__main__":
    # Read CSV file
    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        n = sum(1 for _ in file)
        stop_at = randrange(n)
        file.seek(0)

        for i, row in enumerate(reader, start=1):
            if i >= stop_at:
                set_background(row['Path'])
                break


`