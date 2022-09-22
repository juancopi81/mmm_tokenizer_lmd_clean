# Taken from
# https://www.datacamp.com/tutorial/using-tensorflow-to-compose-music#appendix 

from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
import time

# Define save directory
save_dir = "./custom_midi_dataset/"

# Define URL components
url0 = "https://www.mutopiaproject.org/cgibin/make-table.cgi?startat="
url1 = "&searchingfor=&Composer=&Instrument=Guitar&Style=&collection=&id=&solo=&recent=&timelength=&timeunit=&lilyversion=&preview="

# Set initial values
songNumber = 0
linkCount = 10

# Locate and download each MIDI file
while linkCount > 0:
    url = url0 + str(songNumber) + url1
    html = urlopen(url)
    soup = BeautifulSoup(html.read())
    links = soup.find_all("a")
    linkCount = 0
    for link in links:
        href = link["href"]
        if href.find(".mid") >= 0:
            title = href.split("/")[-1]
            print(title)
            linkCount += 1
            urlretrieve(href, save_dir+title)
    songNumber += 10
    time.sleep(10.0)