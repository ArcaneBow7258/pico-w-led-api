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
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
# # # # #
# For continguous states
class State():
    show = 0
    rainbow = 1
    chase = 2
global_state = State.show
# # # # #
# Tiny Helpers :)
def parse_rgb(arguments):
    return (int(arguments['r']),int(arguments['g']),int(arguments['b']))

# # # # #
# 
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

# # # # #
# General Use
# # # # #
@app.route('/')
async def index(request):
    print('Home Connected')
    return 'Hello, world!'
@app.route('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'
@app.route('/test_pixel')
def test_pixel(request):
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
        return "Test Success"
    except Exception as e:
        return e
# # # # #
# LED Control
# # # # #
args_gb = ['index', 'r','g','b']
@app.route('/pixel', methods =['GET', 'POST'])
async def pixel(request):
    try:
        args = request.args
        if request.method == 'GET':
            if('index' not in args.keys()):
                return 'Please query ann index'
            pixel = np.get_pixel(int(args['index']))
            return f"Pixel at {str(args['index'])} is {pixel}"
        elif request.method == 'POST':
            args_keys = list(set(args_gb) & set(args.keys()))
            print('Testing Args')
            if args_keys.sort() == args_gb.sort():
                print('Has args')
                np.set_pixel(int(args['index']), 
                             parse_rgb(args), 
                              args['brightness'] if 'brightness' in args.keys() else None)
            else:
                return f'Missing Arguments for Set_Pixel: {set(args_gb) - set(args.keys())}'
            return 'POST Finished'
        else:
            return 'Invalid Request Method'
        return "Success"
    except Exception as e:
        return e
@app.route('/brightness', methods =['GET', 'POST'])
def brightness(request):
    try:
        if request.method == 'GET':
            return str(np.brightnessvalue)
        elif request.method == 'POST':
            args = request.args
            if 'value' in args.keys():
                try:
                    int(args['value'])
                except ValueError:
                    print('Please send an integer-like string')
                np.brightness(int(args['value']))
                print("Brightness set to", str(np.brightnessvalue))
            else:
                raise IndexError("value not in query")
            return f'Brightness set to {args["value"]}'
        else:
            return 'Invalid Request Method'
        return "Success"
    except Exception as e:
        return e
@app.route('/show', methods =['POST'])
def show(request):
    if('clear' in request.args.keys()):
        try:
            bit = int(request.args['clear'])
        except ValueError as e:
            print(f'You probably did not send an integer: {e}')
        if(bit == 1):
            np.clear()
            return "Cleared"
        elif(bit == 0):
            np.show()
            global_state=State.show
        else:
            return 'Please send clear bit 0 or 1'
    else:
        np.show()
        global_state=State.show
        print(global_state)
        return 'Shown'
np = Neopixel(num_leds = num_pixels, state_machine = 1, pin = 1, mode = "RGB")
try:
    connect()
except Exception as e:
    print("Error:", e)
    print("Could not connect, will run default LED items.")
    np.brightness(255.0/2)
    np.fill((255, 255, 255))

@app.route('/test_async', methods =['POST'])
async def test_async(request):
    global_state = 1
    while global_state == 1:
        print(f'Waiting: {global_state}')
        await asyncio.sleep(2)
    
# # # # #
# Neopixel Init
# https://docs.micropython.org/en/latest/esp8266/tutorial/neopixel.html
# # # # #


# # # # #
# start app
app.run(port=5001, debug=True)