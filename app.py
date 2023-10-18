#https://microdot.readthedocs.io/en/latest/intro.html
# Flask-like micropython pacakge.
from microdot_asyncio import Microdot
#Need to connect to wifi
import network
# Set up a config.py with said variables
from config import ssid, password, num_pixels, pin  
# LED Controls
# Base neopixel package does not have brightness controll, which I sort of want.
# Please refer to lib to find source, origin github provided.
import machine
from new_neopixel import Neopixel
#Utility
from time import sleep, time

# Seconds to wait before timing out the connection to wifi
timeout = 100
app = Microdot()
def connect():
    global ssid, password
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.config(hostname="picow")
    wlan.active(True)
    wlan.connect(ssid, password)
    start = time()
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
        if ((time() - start) > timeout):
            raise TimeoutError()
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip



@app.route('/')
async def index(request):
    print('Home Connected')
    return 'Hello, world!'

@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'
@app.route('/test_pixel')
async def test_pixel(request):
    try:
        np.brightness(1)
        np.set_pixel(0, (0,0,255)) # B
        np.show()
        sleep(2)
        np.set_pixel(0, (255,0,0)) # G
        np.show()
        sleep(2)
        np.brightness(255)
        np.set_pixel(0, (0,255,0)) # R
        np.show()
        sleep(2)
        print('lower')
        np.brightness(1)
        np.show()
        sleep(2)
        np.clear()
        np.show()
        return "Connect Success"
    except Exception as e:
        return e
        

try:
    connect()
except Exception as e:
    print("Error:", e)
    print("Could not connect, will run default LED items.")
# # # # #
# Neopixel Init
# https://docs.micropython.org/en/latest/esp8266/tutorial/neopixel.html
# # # # #
np = Neopixel(num_leds = num_pixels, state_machine = 1, pin = 1, mode = "RGB")

# # # # #
# start app
app.run(port=5001, debug=True)