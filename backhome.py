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
import BackHomeMessageConfig

CONSUMER_KEY = BackHomeMessageConfig.twkey['cons_key']
CONSUMER_SECRET = BackHomeMessageConfig.twkey['cons_sec']
ACCESS_TOKEN_KEY = BackHomeMessageConfig.twkey['accto_key']
ACCESS_TOKEN_SECRET = BackHomeMessageConfig.twkey['accto_sec']

from datetime import datetime

import math
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def send_dm_callback(gpio_sw):
  gpio_led = 26
  if gpio_sw == BackHomeMessageConfig.button_1['sw'] : 
    gpio_led =  BackHomeMessageConfig.button_1['led']
    msg =      BackHomeMessageConfig.button_1['text']
  if gpio_sw == BackHomeMessageConfig.button_2['sw'] : 
    gpio_led =  BackHomeMessageConfig.button_2['led']
    msg =      BackHomeMessageConfig.button_2['text']
  if gpio_sw == BackHomeMessageConfig.button_3['sw'] : 
    gpio_led =  BackHomeMessageConfig.button_3['led']
    msg =      BackHomeMessageConfig.button_3['text']
  if gpio_sw == BackHomeMessageConfig.button_4['sw'] : 
    gpio_led =  BackHomeMessageConfig.button_4['led']
    msg =      BackHomeMessageConfig.button_4['text']
#  print (gpio_sw,gpio_led,latest_tweet_status) 
  if (GPIO.input(gpio_sw) == GPIO.LOW) and (GPIO.input(gpio_led) == 0) and (latest_tweet_status != u'!OFF'):
#    print (gpio_sw,gpio_led) 
    GPIO.output(gpio_led, True)
    try:
      dm = api.PostDirectMessage(msg + '>> ' + text + current_time_str,BackHomeMessageConfig.account['DM_to'])
      print 'send DM ' + current_time_str + ' ' + msg + '>> ' + text[0:20] + ' ' + str(gpio_sw) + ' ' + str(GPIO.input(gpio_led))
    except:
      print 'can not send DM ' + current_time_str + ' ' + str(gpio_sw)
  return GPIO.input(gpio_led)



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


current_time = datetime.now()
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)
try:
  tweets = api.GetSearch(term=BackHomeMessageConfig.account['special_hash'])
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
latest_tweet_status = latest_tweet.text[0:4]

# Setup button 1
GPIO.setup(BackHomeMessageConfig.button_1['led'], GPIO.OUT)
GPIO.setup(BackHomeMessageConfig.button_1['sw'], GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BackHomeMessageConfig.button_1['sw'], GPIO.RISING, callback=send_dm_callback, bouncetime=200)

# Setup button 2
GPIO.setup(BackHomeMessageConfig.button_2['led'], GPIO.OUT)
GPIO.setup(BackHomeMessageConfig.button_2['sw'], GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BackHomeMessageConfig.button_2['sw'], GPIO.RISING, callback=send_dm_callback, bouncetime=200)

# Setup button 3
GPIO.setup(BackHomeMessageConfig.button_3['led'], GPIO.OUT)
GPIO.setup(BackHomeMessageConfig.button_3['sw'], GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BackHomeMessageConfig.button_3['sw'], GPIO.RISING, callback=send_dm_callback, bouncetime=200)

# Setup button 4
GPIO.setup(BackHomeMessageConfig.button_4['led'], GPIO.OUT)
GPIO.setup(BackHomeMessageConfig.button_4['sw'], GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BackHomeMessageConfig.button_4['sw'], GPIO.RISING, callback=send_dm_callback, bouncetime=200)

# Initialize button 
GPIO.output(BackHomeMessageConfig.button_1['led'], False)
GPIO.output(BackHomeMessageConfig.button_2['led'], False)
GPIO.output(BackHomeMessageConfig.button_3['led'], False)
GPIO.output(BackHomeMessageConfig.button_4['led'], False)



# Animate text moving in sine wave.
print('Press Ctrl-C to quit.')
pos = startpos
while True:
    # get current time
    current_time = datetime.now()
    current_time_str = current_time.strftime(u"%m/%d %H:%M")

#    print(GPIO.input(BackHomeMessageConfig.button_1['sw']), \
#          GPIO.input(BackHomeMessageConfig.button_1['led']),\
#          GPIO.input(BackHomeMessageConfig.button_2['sw']),\
#          GPIO.input(BackHomeMessageConfig.button_2['led']),\
#          GPIO.input(BackHomeMessageConfig.button_3['sw']),\
#          GPIO.input(BackHomeMessageConfig.button_3['led']),\
#          GPIO.input(BackHomeMessageConfig.button_4['sw']),\
#          GPIO.input(BackHomeMessageConfig.button_4['led']))
    
    # get tweets
    if current_time.second == 0:
      try:
        tweets = api.GetSearch(term=BackHomeMessageConfig.account['special_hash'])
        latest_tweet = tweets[0]
        if (latest_tweet_id <> latest_tweet.id):
          latest_tweet_id = latest_tweet.id
          latest_tweet_status = latest_tweet.text[0:4]
          GPIO.output(BackHomeMessageConfig.button_1['led'], False)
          GPIO.output(BackHomeMessageConfig.button_2['led'], False)
          GPIO.output(BackHomeMessageConfig.button_3['led'], False)
          GPIO.output(BackHomeMessageConfig.button_4['led'], False)
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

