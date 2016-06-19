# coding: utf-8
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import RPi.GPIO as GPIO


import twitter
import twitkey

CONSUMER_KEY = twitkey.twkey['cons_key']
CONSUMER_SECRET = twitkey.twkey['cons_sec']
ACCESS_TOKEN_KEY = twitkey.twkey['accto_key']
ACCESS_TOKEN_SECRET = twitkey.twkey['accto_sec']

from datetime import datetime

import math
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# 128x32 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Initialize library.
disp.begin()

# Get display width and height.
width = disp.width
height = disp.height

# Clear display.
disp.clear()
disp.display()

# Create image buffer.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (width, height))

# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as this python script!
# Some nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/home/pi/work/BackHomeMessage/TakaoGothic.ttf', 24)

# Create drawing object.
draw = ImageDraw.Draw(image)

# Define text and get total width.
#text = 'SSD1306 ORGANIC LED DISPLAY. THIS IS AN OLD SCHOOL DEMO SCROLLER!! GREETZ TO: LADYADA & THE ADAFRUIT CREW, TRIXTER, FUTURE CREW, AND FARBRAUSCH'
text = '日本語表示のテスト'
maxwidth, unused = draw.textsize(text, font=font)

# Set animation and sine wave parameters.
# amplitude = height/4
# offset = height/2 - 4
amplitude = 0
offset = 0
velocity = -2
startpos = width


# get tweets
#api = twitter.Api(consumer_key=CONSUMER_KEY,
#                  consumer_secret=CONSUMER_SECRET,
#                  access_token_key=ACCESS_TOKEN_KEY,
#                  access_token_secret=ACCESS_TOKEN_SECRET)
#tweets = api.GetSearch(term=u"#一郎帰宅")
#
#text = u""
current_time = datetime.now()
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)
try:
  tweets = api.GetSearch(term=u"#一郎帰宅")
  latest_tweet = tweets[0]
  if (current_time.second - latest_tweet.created_at_in_seconds < 43200) and (latest_tweet.text[0:4] != u'!OFF') :  # 12 hours 
  #  print(latest_tweet.text[0:4])
    dt = time.strftime(u"%m/%d %H:%M",time.localtime(latest_tweet.created_at_in_seconds))
    text = latest_tweet.text
    text = text[0:-5] + u' ' + dt
  else:
    text = u''
except:  
  text = u''


latest_tweet_id = latest_tweet.id

gpio_led_1=17
gpio_sw_1=18

GPIO.setup(gpio_led_1, GPIO.OUT)
GPIO.setup(gpio_sw_1, GPIO.IN)


GPIO.output(gpio_led_1, False)
print(GPIO.input(gpio_led_1))
#GPIO.output(gpio_led_1, True)
#print(GPIO.input(gpio_led_1))


# Animate text moving in sine wave.
print('Press Ctrl-C to quit.')
pos = startpos
while True:
    # get current time
    current_time = datetime.now()
    current_time_str = current_time.strftime(u"%m/%d %H:%M")

    if (GPIO.input(gpio_sw_1) == 1) and (GPIO.input(gpio_led_1) == 0):
      print('DM button pushed!')
      GPIO.output(gpio_led_1, True)
      try:
        dm = api.PostDirectMessage(u'了解 ' + current_time_str,u'76076870')
        print('send DM' + current_time_str)
        print(GPIO.input(gpio_led_1))
      except:
        print('can not send DM ' + current_time_str)
#    else:
#      GPIO.output(gpio_led_1, False)

    # get tweets
    if current_time.second == 0:
#      api = twitter.Api(consumer_key=CONSUMER_KEY,
#                  consumer_secret=CONSUMER_SECRET,
#                  access_token_key=ACCESS_TOKEN_KEY,
#                  access_token_secret=ACCESS_TOKEN_SECRET)
      try:
        tweets = api.GetSearch(term=u"#一郎帰宅")
        latest_tweet = tweets[0]
        if (latest_tweet_id <> latest_tweet.id):
          GPIO.output(gpio_led_1, False)
          latest_tweet_id = latest_tweet.id
        if (current_time.second - latest_tweet.created_at_in_seconds < 43200) and (latest_tweet.text[0:4] != u'!OFF') :  # 12 hours 
#          print(latest_tweet.text[0:4])
          dt = time.strftime(u"%m/%d %H:%M",time.localtime(latest_tweet.created_at_in_seconds))
          text = latest_tweet.text
          text = text[0:-5] + u' ' + dt
        else:
          text = u''
      except:
        text = u''

    # Clear image buffer by drawing a black filled box.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    # Enumerate characters and draw them offset vertically based on a sine wave.
    x = pos
    maxwidth, unused = draw.textsize(text, font=font)
#    for i, c in enumerate(text.decode('utf-8')):
    for i, c in enumerate(text):
        # Stop drawing if off the right side of screen.
        if x > width:
            break
        # Calculate width but skip drawing if off the left side of screen.
        if x < -10:
            char_width, char_height = draw.textsize(c, font=font)
            x += char_width
            continue
        # Calculate offset from sine wave.
        y = offset+math.floor(amplitude*math.sin(x/float(width)*2.0*math.pi))
        # Draw text.
        draw.text((x, y), c, font=font, fill=255)
        # Increment x position based on chacacter width.
        char_width, char_height = draw.textsize(c, font=font)
        x += char_width
    # Draw the image buffer.
    disp.image(image)
    disp.display()
    # Move position for next frame.
    pos += velocity
    # Start over if text has scrolled completely off left side of screen.
    if pos < -maxwidth:
        pos = startpos
    # Pause briefly before drawing next frame.
    time.sleep(0.05)

