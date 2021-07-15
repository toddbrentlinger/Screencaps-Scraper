import requests
import time
import json
import math
import pprint

import shutil

import os

from bs4 import BeautifulSoup

# FanCaps.net
def scrapeFanCapsURL(url, title):
    """
    Downloads screencaps of movie from FanCaps.net into folder.
    @params:
        url     -Required : address to specific movie on FanCaps.net (Str)
        title   -Required : title of the movie (Str)
    """

    # List to hold individual image urls
    imageURLList = []

    isLastPage = False
    page = 0
    while not isLastPage:
        # BeautifulSoup content
        content = getBeautifulSoupContent(url)
        
        page += 1
        print('Scraping page: ', page, end='\r')

        for row in content.find(class_="middle_bar").find_all(class_="row"):
            for link in row.find_all('a'):
                imageID = link['href'].split('imageid=', 1)[1]
                imageURLList.append('https://cdni.fancaps.net/file/fancaps-movieimages/' + imageID + '.jpg')

        # Check if last page. If not, increment url to next page
        lastPaginationLink = content.find(class_="pagination").find_all('li')[-1].find('a')
        if (lastPaginationLink['href'].startswith('#')):
            isLastPage = True
        else:
            url = 'https://fancaps.net/movies/' + lastPaginationLink['href']

    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(imageURLList)

    downloadImagesFromURLList(imageURLList, title)

    # Write image urls to JSON file
    #with open(title.replace(' ', '_') + '_FancapsScreencapImageUrls.json', 'w') as outfile:
    #    json.dump(imageURLList, outfile, indent=4)

# Creates folder in specified directory location
def createDirectory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        print('Created Directory: ', dir)
    else:
        print('Directory Already Exists: ', dir)
    return dir

def getBeautifulSoupContent(url):
    response = requests.get(url, timeout=5)
    time.sleep(.3) # Wait after request to limit time between next response
    if not response:
        raise Exception("No response from: ", url)
    return BeautifulSoup(response.content, 'html.parser')

def downloadImagesFromURLList(imageURLList, title):
    total = len(imageURLList)
    current = 0

    # Create folder at current directory with title argument as the name
    urlPrepend = createDirectory(title) + '/'

    for imageURL in imageURLList:
        filename = imageURL.split("/")[-1]

        # Open the url image, set stream to True, this will return the stream content
        r = requests.get(imageURL, stream = True)
        time.sleep(.3) # Wait after request to limit time between next response

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
    
            # Open a local file with wb ( write binary ) permission.
            with open(urlPrepend + filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            current += 1
            print('Image sucessfully Downloaded: ', filename, ' (', current, '/', total, ')', end='\r')
        else:
            print('Image Couldn\'t be retreived from url: ', imageURL)

def downloadImagesFromJSON(url, urlPrepend):
    with open(url, 'r') as outfile:
        imageURLList = json.load(outfile)
        downloadImagesFromURLList(imageURLList, urlPrepend)

def main():
    # Elapsed Time - Start
    startTime = time.time()

    scrapeFanCapsURL('https://fancaps.net/movies/MovieImages.php?name=Kick_Ass_2&movieid=528', 'Kick-Ass 2')
    #scrapeFanCapsURL('https://fancaps.net/movies/MovieImages.php?name=Tom_and_Jerry_2021&movieid=2392', 'Tom and Jerry')
    #scrapeFanCapsURL('https://fancaps.net/movies/MovieImages.php?name=Cruella_2021&movieid=2753', 'Cruella')

    # Elapsed Time - End
    timeElapsed = time.time() - startTime
    print('\nTime Elapsed: ', math.floor(timeElapsed / 60), 'min:', math.floor(timeElapsed % 60), 'sec')

if __name__ == '__main__':
    main()