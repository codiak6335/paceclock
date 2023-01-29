# Clock example with NTP synchronization
#
# Create a secrets.py with your Wifi details to be able to get the time
# when the Galactic Unicorn isn't connected to Thonny.
#
# secrets.py should contain:
# WIFI_SSID = "Your WiFi SSID"
# WIFI_PASSWORD = "Your WiFi password"
#
# Clock synchronizes time on start, and resynchronizes if you press the A button
import _thread
import time
import math
import machine
import network
import ntptime
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
from microdot import Microdot, send_file
import json


app = Microdot()

try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
    wifi_available = True
except ImportError:
    print("Create secrets.py with your WiFi credentials to get time from NTP")
    wifi_available = False


# create galactic object and graphics surface for drawing
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

# create the rtc object
rtc = machine.RTC()

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# set up some pens to use later
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)
SKYBLUE = graphics.create_pen(52, 232, 235)
PURPLE = graphics.create_pen(143, 52, 235)
penc = PURPLE


def do_access_point():
    ssid = "PicoW"
    password = "123456789"

    ap = network.WLAN(network.AP_IF)
    # ap.active(True)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while not ap.active:
        pass

    print("Access point active")
    print(ap.ifconfig())
    return ap


# noinspection SpellCheckingInspection
def do_connect():
    #ssid = 'beaver'
    #key = 'joanieandcharlielovealex'
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        print(WIFI_SSID)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    return sta_if

# Connect to wifi and synchronize the RTC time from NTP
def sync_time(): 
    if not wifi_available:
        return
    #wlan = None
    # Start connection
    wlan = do_connect()
    #wlan = do_access_point()
    #wlan = network.WLAN(network.STA_IF)
    #wlan.active(True)
    #wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connect success or failure
    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(0.2)

    if max_wait > 0:
        print("Connected")
        print(wlan.ifconfig())
        try:
            ntptime.settime()
            print("Time set")
        except OSError:
            pass

#    wlan.disconnect()
#    wlan.active(False)
    print("1")

# NTP synchronizes the time to UTC, this allows you to adjust the displayed time
# by one hour increments from UTC by pressing the volume up/down buttons
#
# We use the IRQ method to detect the button presses to avoid incrementing/decrementing
# multiple times when the button is held.
utc_offset = 0


year, month, day, wd, hour, minute, second, _ = rtc.datetime()

last_second = second


# Check whether the RTC time has changed and if so redraw the display


gu.set_brightness(.5)

sync_time()





zero_bits = [
   0x1e, 0x00, 0x3f, 0x00, 0x33, 0x00, 0x33, 0x00, 0x33, 0x00, 0x33, 0x00,
   0x33, 0x00, 0x33, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
one_bits = [
   0x08, 0x00, 0x0c, 0x00, 0x0f, 0x00, 0x0f, 0x00, 0x0c, 0x00, 0x0c, 0x00,
   0x0c, 0x00, 0x0c, 0x00, 0x0c, 0x00, 0x3f, 0x00, 0x3f, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
two_bits = [
   0x1e, 0x00, 0x3f, 0x00, 0x33, 0x00, 0x30, 0x00, 0x30, 0x00, 0x1c, 0x00,
   0x0e, 0x00, 0x07, 0x00, 0x03, 0x00, 0x3f, 0x00, 0x3f, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
three_bits = [
   0x1e, 0x00, 0x3f, 0x00, 0x33, 0x00, 0x30, 0x00, 0x3c, 0x00, 0x3c, 0x00,
   0x30, 0x00, 0x30, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
four_bits = [
   0x30, 0x00, 0x38, 0x00, 0x3c, 0x00, 0x36, 0x00, 0x33, 0x00, 0x33, 0x00,
   0x3f, 0x00, 0x3f, 0x00, 0x30, 0x00, 0x30, 0x00, 0x30, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
five_bits = [
   0x3f, 0x00, 0x3f, 0x00, 0x03, 0x00, 0x03, 0x00, 0x1f, 0x00, 0x3e, 0x00,
   0x30, 0x00, 0x33, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
six_bits = [
   0x1c, 0x00, 0x3e, 0x00, 0x07, 0x00, 0x03, 0x00, 0x03, 0x00, 0x1f, 0x00,
   0x3f, 0x00, 0x33, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
seven_bits = [
   0x3f, 0x00, 0x3f, 0x00, 0x30, 0x00, 0x30, 0x00, 0x18, 0x00, 0x0c, 0x00,
   0x06, 0x00, 0x06, 0x00, 0x06, 0x00, 0x06, 0x00, 0x06, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
eight_bits = [
   0x1e, 0x00, 0x3f, 0x00, 0x33, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00,
   0x3f, 0x00, 0x33, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
nine_bits = [
   0x1e, 0x00, 0x3f, 0x00, 0x33, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x3e, 0x00,
   0x30, 0x00, 0x30, 0x00, 0x33, 0x00, 0x3f, 0x00, 0x1e, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
colon_bits = [
   0x00, 0x00, 0x00, 0x00, 0x06, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x06, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

ary = {'0':zero_bits,'1':one_bits,'2':two_bits,'3':three_bits,'4':four_bits,'5':five_bits,'6':six_bits,'7':seven_bits,'8':eight_bits,'9':nine_bits,':':colon_bits}


last_total_seconds = time.time()
clockmode = True

def printZero(x1,y1):

    global year, month, day, wd, hour, minute, second, last_second

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()

    
    if second != last_second:
        hour += utc_offset

        

        clock = "{:02}:{:02}:{:02}".format(hour, minute, second)


        total_seconds = time.time()


        elapsed_seconds = total_seconds - last_total_seconds

        m, s = divmod(elapsed_seconds, 60)
        h, m = divmod(m, 60)
        if not clockmode:
            clock = "{:02}:{:02}:{:02}".format(h, m, s)



        last_second = second

        clock_screen_positions = [0,7,13,17,24,30,34,41]
        c = 0
        str1 = clock
        graphics.set_pen(BLACK)
        graphics.clear()
        graphics.set_pen(penc)
        for x in str1:
            for y in range(11):
                st = ''
                for b in range(8):
                    if ary[x][y*2] & (1 << b):
                        graphics.pixel(b+x1+clock_screen_positions[c]+3, y+y1)
            c+=1
        


def start_pace_clock_thread():
    while True:
        if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
            gu.adjust_brightness(+0.01)

        if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
            gu.adjust_brightness(-0.01)

        if gu.is_pressed(GalacticUnicorn.SWITCH_A):
            sync_time()

        #redraw_display_if_reqd()
        printZero(0,0)
        # update the display
        gu.update(graphics)

        time.sleep(0.2)
    
@app.route('/')
def index(request):
    return send_file("ftla-paceclock.html")
# noinspection PyUnusedLocal

@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)

@app.route('/resetpace')
def reset_pace(request):
    global last_total_seconds, clockmode
    last_total_seconds = time.time()
    clockmode = False

gu.set_brightness(.5)

@app.route('/bright')
def bright(request):
    gu.set_brightness(1)
@app.route('/dim')
def dim(request):
    gu.set_brightness(.1)	
@app.route('/normal')
def normal(request):
    gu.set_brightness(.5)
    
@app.get('/color/<string:colors>')
def color(request, colors):
    global penc
    print(colors)  
    c = colors.split(',')
    penc = graphics.create_pen(int(c[0]),int(c[1]),int(c[2]))
   
@app.route('/togglemode')
def togglemode(request):
    global clockmode
    clockmode = not clockmode

_thread.start_new_thread(start_pace_clock_thread, ())
time.sleep(3)
app.run(debug=True, port=80)
