#https://microdot.readthedocs.io/en/latest/intro.html
# Flask-like micropython pacakge.
from microdot_asyncio import Microdot
# Set up a config.py with said variables
from config import num_pixels, pin  
# LED Controls
# Base neopixel package does not have brightness controll, which I sort of want.
# Please refer to lib to find source, origin github provided.
import machine
from new_neopixel import Neopixel
#Utility
from time import sleep, time
try:
    import uasyncio as asyncio
    #print('imported uasyncio')
except ImportError:
    import asyncio
# Connection Stuff
from connect import connect, ap
# # # # #
# For continguous 
# # # # #
class State():
    show = 0
    rainbow = 1
    chase = 2
global_state = State.show
event_state = asyncio.Event()
control_lock = asyncio.Lock()
def event_trigger(state = State.show):
    global_state = state
    event_state.set()
    

# # # # #
# Tiny Helpers :)
def parse_rgb(arguments):
    return (int(arguments['r']),int(arguments['g']),int(arguments['b']))
def list_compare(input_list, control_List):
    merged = list(set(input_list) & set(control_List))
    return merged.sort() == control_List.sort()  

# # # # #
# Create App
app = Microdot()


# # # # #
# General Use
# # # # #
@app.route('/')
async def index(request):
    print('Home Connected')
    return 'Hello, world!'
@app.route('/shutdown', methods=['POST'])
async def shutdown(request):
    if request.method == 'POST':
        request.app.shutdown()
        return 'The server is shutting down...'
@app.route('/test_pixel')
# Redirects
# microsoft windows redirects
@app.route("/ncsi.txt")
async def ncsi(request):
    print("AP ncsi.txt request received")
    return index(request), 200

@app.route("/connecttest.txt")
async def connecttest(request):
    print("AP connecttest.txt request received")
    return index(request), 200

@app.route("/redirect")
async def redirect(request):
    print("AP redirect request received")
    return index(request), 302

# android redirects
@app.route("/generate_204")
async def generate_204(request):
    print("AP generate_204 request received")
    return index(request), 302

# apple redir
@app.route("/hotspot-detect.html")
async def hotspot(request):
    print("AP hotspot-detect.html request received")
    return "Apple"
# Error handler
@app.errorhandler(404)
async def not_found(request):
    return {'error': 'resource not found'}, 404

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
args_pixel = ['index', 'r','g','b']
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
            args_keys = list(set(args_pixel) & set(args.keys()))
            print('Testing Args')
            if list_compare(args_keys, args_pixel):
                print('Has args')
                np.set_pixel(int(args['index']), 
                             parse_rgb(args), 
                              args['brightness'] if 'brightness' in args.keys() else None)
            else:
                return f'Missing Arguments for Set_Pixel: {set(args_pixel) - set(args.keys())}'
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
            event_trigger()
        else:
            return 'Please send clear bit 0 or 1'
    else:
        np.show()
        event_trigger()
        print('State:', global_state)
        return 'Shown'
args_gb = ['r','g','b']
@app.route('/fill', methods =['POST'])
async def fill(request):
    args = request.args
    if request.method == 'POST':
        if list_compare(args.keys(), args_gb):
            np.fill(parse_rgb(args), args['brightness'] if 'brightness' in args.keys() else None)
        else:
            return 'Missing Args'
    return 'Done'



# # # # # 
# Actual Code Running

np = Neopixel(num_leds = num_pixels, state_machine = 1, pin = 1, mode = "RGB")
try:
    connect()
    # If you rerun code you have to hard reset to disable the AP and reset config.
    ap(catchall=True)
except Exception as e:
    print("Error connecting:", e)
    print("Could not connect, will run default LED items.")
    np.brightness(255.0/2)
    np.fill((255, 255, 255))

@app.route('/test_async', methods =['POST'])
async def test_async(request):
    global_state = State.chase
    control_lock.acquire()
    while not event_state.is_set():
        print(f'Waiting: {global_state}')
        await asyncio.sleep(2)
    control_lock.release()
    return "Killed!"
    
# # # # #
# Neopixel Init
# https://docs.micropython.org/en/latest/esp8266/tutorial/neopixel.html
# # # # #


# # # # #
# start app
app.run(port=80, debug=True)