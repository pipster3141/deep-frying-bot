"""
Deep Frying Bot inteded to work on Dank Memes.
First bot I have created so please give feedback!
"""

import random
import time

import praw
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
from imgurpython import ImgurClient
import configparser

import bs4, urllib3, requests, lxml
from bs4 import BeautifulSoup
urllib3.disable_warnings()



def deepfry(url):
    #the degree is how deep fryed it will be
    degree = 3

    fileType = url.split(".")[1]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = image.convert('RGBA')

    #Add emojis and making sure they're transparent
    b = Image.open('bButton.png')
    b = b.convert('RGBA')
    
    laughing = Image.open('laughing.png')
    laughing = laughing.convert('RGBA')
    
    okay = Image.open('okay.png')
    okay = okay.convert('RGBA')
    
    emojis = [b, laughing, okay]

    for i in range(3):
        #Choose a random emoji
        emojiOfChoice = random.choice(emojis)

        #resizing
        emojiOfChoice = emojiOfChoice.resize((int(image.width/10),int(image.height/10)))

        #rotation
        angle = random.randint(-20,20)
        if angle < 0:
            angle += 360
        emojiOfChoice = emojiOfChoice.rotate(angle)

        #decide on x and y position and paste
        maxY = int(image.height*.8)
        yPosition = random.randint(0, maxY)

        maxX = int(image.width*.8)
        xPosition = random.randint(0, maxX)
        
        image.paste(emojiOfChoice, (xPosition, yPosition), emojiOfChoice)
    
    #Apply red filter if degree greater than or equal to 4
    redImage = Image.new('RGBA', image.size, (255,0,0,0))
    image = Image.blend(image, redImage, (.10))

    #Increase contrast
    eContrast = ImageEnhance.Contrast(image)
    image = eContrast.enhance(degree)

    #Increase saturation
    eSaturation = ImageEnhance.Color(image)
    image = eSaturation.enhance(degree)

    #Increase brightness
    eBrightness = ImageEnhance.Brightness(image)
    image = eBrightness.enhance(degree)
    
    #Decrease quality
    image = image.convert('RGB')
    
    return image

def urlFromPermalink(permalink):
    soup = getHTML('www.reddit.com'+permalink)
    #get all anchor tags in the HTML and get ones with links in them
    for anchor in soup.find_all('a'):
        link = anchor.get('href')
        try:
            #try to get a built in reddit link for it
            if 'i.redd.it' in link:
                #always take png format first since it's higher quality
                if '.png' in link:
                    return link
                elif '.jpg' in link:
                    return link
        except:
            #if that doesn't work I guess imgur will do
            if '.png' in link:
                return link
            elif '.jpg' in link:
                return link
    return

def getHTML(url):
    http = urllib3.PoolManager()
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data, 'lxml')
    return soup    
    
    
def main():

    #creating my config parser
    config = configparser.ConfigParser()
    config.read('auth.ini')

    #instantiating the bot
    bot = praw.Reddit(client_id = config.get('redditCredentials', 'client_id'),
                      client_secret = config.get('redditCredentials', 'client_secret'),
                      password = config.get('redditCredentials', 'password'),
                      user_agent = config.get('redditCredentials', 'agent'),
                      username = config.get('redditCredentials', 'username'))

    #the subreddit I want the bot to be on
    subreddit = bot.subreddit('dankmeme')

    #phrase people will activate my bot with
    keyphrase = "!deepfry"

    #now I analyze every submission and see if it has the keyphrase
    #if it does, I can go ahead an deepfry and save it

    for comment in subreddit.stream.comments():
        if keyphrase in comment.body and comment.is_root:

            try:
                #if a comment calls the bot I grab the post and deep fry
                parent = comment.parent()
                url = urlFromPermalink(parent.permalink)
                image = deepfry(url)

                path = 'fried.jpg'
                image.save(path,format="JPEG",optimize=True,quality=30)
                    
                imgurClient = ImgurClient(config.get('imgurCredentials', 'client_id'),
                                          config.get('imgurCredentials', 'client_secret'))

                response = imgurClient.upload_from_path(path)
                link = response['link']
                comment.reply("[Here]("+link+") is your deep fried meme")
                
            except:
                #If it doesn't work I give an error message
                comment.reply("Whoops sorry I wasn't able to deep fry this image")
        
    

if __name__ == "__main__":
    main()
