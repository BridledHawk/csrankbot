import discord
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
import sqlite3
import http.client

GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

def createConn():
    conn = sqlite3.connect("users.db")
    return(conn)


async def getImg(uid, channel):
    print('Fetching ranks for '+uid)
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.binary_location = GOOGLE_CHROME_PATH
    driver = webdriver.Chrome(execution_path=CHROMEDRIVER_PATH, chrome_options=options)
    driver.get("https://csgostats.gg/player/"+uid+"#/live")
    driver.set_window_size(1920, 1080)
    try:
        element = driver.find_element_by_id('live-match-section') # find part of the page you want image of
        location = element.location
        size = element.size
        png = driver.get_screenshot_as_png() # saves screenshot of entire page
        driver.quit()
        
        im = Image.open(BytesIO(png)) # uses PIL library to open image in memory

        left = location['x'] + 200
        top = location['y'] + 12
        right = location['x'] + size['width'] - 320
        bottom = location['y'] + size['height'] - 24


        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save("ranks.png")
        await channel.send(file=discord.File("ranks.png"))
    except:
        await channel.send("Could Not fetch ranks. This is likely due to an invalid steamID64 being set. You can set your steam64ID using .setID")


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))


        if message.content.startswith(".setid"):
            args = message.content.split()
            if(len(args) >= 2):
                #check exists
                conn = createConn()
                c = conn.cursor()
                c.execute('SELECT * FROM users WHERE discordID = "%s"' % message.author)
                result = c.fetchone()
                if result:
                    #alter
                    c.execute('UPDATE users SET steamID = "%s" WHERE discordID = "%s";' % (args[1], message.author))
                    await message.channel.send("Your steamID64 has been changed from \"%s\" to \"%s\"" % (result[1], args[1]))
                else:
                    #add
                    c.execute('INSERT INTO users (discordID,steamID) VALUES ("%s","%s");' % (message.author, args[1]))
                    await message.channel.send("Your steamID64 has been set to \"%s\"" % args[1])

                conn.commit()
                conn.close()
            else:
                await message.channel.send("Please set an ID")



        



        if message.content == ".ranks":
            conn = createConn()
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE discordID = "%s"' % message.author)
            result = c.fetchone()
            conn.close()
            if result:
                await message.channel.send("Fetching...")
                await getImg(result[1], message.channel)
            else:
                await message.channel.send("Your steamID64 is not set! Please set it using the .setid command.")







client = MyClient()
client.run(token)

