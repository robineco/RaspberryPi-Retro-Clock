import time
from datetime import datetime
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment
import RPi.GPIO as GPIO
from newsapi import NewsApiClient
from gtts import gTTS
import os
from pygame import mixer


# debug mode
debug_mode = False

# api config
NEWS_API_KEY = 'API KEY FROM NEWS-API'
NEWS_API_NUMBER_HEADLINES = 4
NEWS_API_COUNTRY = 'de'
GTTS_LANGUAGE = 'de'
GTTS_SOUND_FILE_NAME = 'news.mp3'

# server status config
HOSTS = ['example.de', 'google.de']

# button mapping
BUTTON_ONE = 16
BUTTON_TWO = 20
BUTTON_THREE = 21

# display brightness mapping
BRIGHTNESS_MORNING = 64
BRIGHTNESS_MIDDAY = 255
BRIGHTNESS_NIGH = 16

# create seven segment device
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=1)
seg = sevensegment(device)
seg.device.contrast(BRIGHTNESS_MORNING)


def ping(host):
    print('DEBUG: Ping host: %s', host) if debug_mode else ''

    response = os.system("ping -c 1 " + host)
    if response == 0:
        print('DEBUG:', host, 'is up!') if debug_mode else ''
        return 'UP'
    else:
        print('DEBUG:', host, 'is down!') if debug_mode else ''
        return 'DW'


def play_headlines():
    print('DEBUG: Playing top news headlines') if debug_mode else ''

    news_api = NewsApiClient(api_key=NEWS_API_KEY)
    top_headlines = news_api.get_top_headlines(country=NEWS_API_COUNTRY)
    title = ''

    for i in range(NEWS_API_NUMBER_HEADLINES):
        title += top_headlines['articles'][i]['title'] + '\n'

    print(title) if debug_mode else ''

    speech = gTTS(text=title, lang=GTTS_LANGUAGE, slow=False)
    speech.save(GTTS_SOUND_FILE_NAME)
    mixer.init()
    mixer.music.load(GTTS_SOUND_FILE_NAME)
    mixer.music.play()


def button_one(channel):
    print('DEBUG: Button One pressed') if debug_mode else ''

    GPIO.remove_event_detect(BUTTON_ONE)
    time.sleep(0.4)
    GPIO.add_event_detect(BUTTON_ONE, GPIO.RISING, callback=button_one)

    play_headlines()


def button_two():
    print('DEBUG: Button Two pressed') if debug_mode else ''

    GPIO.remove_event_detect(BUTTON_TWO)
    time.sleep(0.4)
    GPIO.add_event_detect(BUTTON_TWO, GPIO.RISING, callback=button_two)

    status = ping(HOSTS[0])
    seg.text = ''
    seg.text = 'CLOUD ' + status
    time.sleep(3)

    status = ping(HOSTS[1])
    seg.text = ''
    seg.text = 'GOOGLE' + status
    time.sleep(3)


def button_three(channel):
    print('DEBUG: Button Three pressed') if debug_mode else ''

    GPIO.remove_event_detect(BUTTON_THREE)
    time.sleep(0.4)
    GPIO.add_event_detect(BUTTON_THREE, GPIO.RISING, callback=button_three)


def display_print_date():
    print('DEBUG: Printing date on display') if debug_mode else ''

    seg.text = ''
    now = datetime.now()
    seg.text = now.strftime("%d-%m-%y")
    time.sleep(5)


def display_print_time():
    # print('DEBUG: Printing time on display') if debug_mode else ''

    now = datetime.now()
    current_hour = now.hour
    # change brightness depending on time
    if 6 < current_hour < 9:
        seg.device.contrast(BRIGHTNESS_MORNING)
    elif 9 < current_hour < 22:
        seg.device.contrast(BRIGHTNESS_MIDDAY)
    else:
        seg.device.contrast(BRIGHTNESS_NIGH)

    current_time = now.strftime("%H-%M-%S")
    # print('DEBUG: current_time %s', current_time) if debug_mode else ''
    seg.text = current_time


def main():
    if debug_mode:
        print('------------------------------------------')
        print('-------- DISPLAY CLOCK - ROBINECO --------')
        print('--------   DEBUG MODE ACTIVATED   --------')
        print('------------------------------------------')

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_ONE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_ONE, GPIO.RISING, callback=button_one)
    GPIO.setup(BUTTON_TWO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_TWO, GPIO.RISING, callback=button_two)
    GPIO.setup(BUTTON_THREE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_THREE, GPIO.RISING, callback=button_three)

    date_counter = 0
    while True:
        print('DEBUG: date_counter:', date_counter) if debug_mode else ''
        display_print_time()
        date_counter += 1
        if date_counter >= 250:
            button_two()
            date_counter = 0
        if date_counter == 150:
            display_print_date()
        time.sleep(0.2)


if __name__ == '__main__':
    main()

