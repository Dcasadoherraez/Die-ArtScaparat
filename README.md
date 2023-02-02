# 🎨🖌️ Die ArtScaparat 🎨🖌️

Learn art easy and unconsciously! _🎨🖌️ Die ArtScaparat 🎨🖌️_ will give you a new masterpiece as your wallpaper every time you turn on your Linux PC.
It even shows the title and artist!

![Drag Racing](Dragster.jpg)

## Requirements

```
pip install beautifulsoup4 unidecode
```

## How to use it

### 1. Get a bunch of masterpieces

```
python3 downloader.py
```

### 2. Set the background to your launch script
1. Search for `Startup Applications` in Ubuntu.
2. Click `Add`
3. Name: `Die ArtScaparat`, Command: `python3 <local-path-to-repo>/Die-ArtScaparat/changer.py`
4. Change the background format in the terminal: `gsettings set org.gnome.desktop.background picture-options 'scaled'`

### 3. Done! Ready to impress everyone with your knowledge on masterpieces 🎨🖌️👨‍🎨

_DISCLAIMER: The purpose of this project is fullly educational! No intention to steal or claim as mine any of the incredible masterpieces from `https://artvee.com/`_
